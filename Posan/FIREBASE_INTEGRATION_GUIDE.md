# 🔥 Firebase Integration for Study Plan Persistence

## Overview

This guide shows how to persist study plan outputs (uploaded PDFs, generated questions, and results) to Firebase.

---

## 🎯 What Will Be Persisted

1. **Uploaded PDFs** → Firebase Storage
2. **Generated Questions** → Firestore Database
3. **Student Answers & Grades** → Firestore Database
4. **Study Plan Metadata** → Firestore Database
5. **User Progress** → Firestore Database

---

## 📦 Architecture

```
Frontend (React)
    ↓
Backend (FastAPI)
    ↓
Firebase Admin SDK
    ↓
Firebase Cloud
    ├── Storage (PDFs)
    └── Firestore (Data)
```

---

## 🚀 Step 1: Setup Firebase Project

### 1.1 Create Firebase Project
1. Go to https://console.firebase.google.com/
2. Click "Add Project"
3. Name it: "POSAN-Study-Assistant"
4. Enable Google Analytics (optional)
5. Click "Create Project"

### 1.2 Enable Services
1. **Storage**: 
   - Go to Build → Storage
   - Click "Get Started"
   - Choose "Start in test mode"
   - Click "Done"

2. **Firestore**:
   - Go to Build → Firestore Database
   - Click "Create Database"
   - Choose "Start in test mode"
   - Select location (closest to your users)
   - Click "Enable"

### 1.3 Get Service Account Key
1. Go to Project Settings (⚙️ icon)
2. Go to "Service Accounts" tab
3. Click "Generate New Private Key"
4. Save the JSON file as `firebase-credentials.json`
5. **IMPORTANT**: Keep this file secure! Don't commit to Git!

---

## 🔧 Step 2: Install Firebase Admin SDK

### Backend (Python)
```bash
cd backend
pip install firebase-admin
```

### Update requirements.txt
```bash
echo "firebase-admin==6.3.0" >> requirements.txt
```

---

## 📝 Step 3: Backend Implementation

### 3.1 Create Firebase Service (`backend/app/services/firebase_service.py`)

```python
"""
Firebase Service for Study Plan Persistence
"""
import firebase_admin
from firebase_admin import credentials, storage, firestore
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import os
from pathlib import Path

class FirebaseService:
    """Service for Firebase Storage and Firestore operations"""
    
    def __init__(self):
        # Initialize Firebase Admin SDK
        cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')
        
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {
                'storageBucket': 'posan-study-assistant.appspot.com'  # Replace with your bucket
            })
        
        self.db = firestore.client()
        self.bucket = storage.bucket()
    
    # ==================== STORAGE OPERATIONS ====================
    
    def upload_pdf(
        self, 
        file_path: str, 
        user_id: str, 
        material_id: str
    ) -> str:
        """
        Upload PDF to Firebase Storage
        
        Returns: Public URL of uploaded file
        """
        blob_name = f"study_materials/{user_id}/{material_id}.pdf"
        blob = self.bucket.blob(blob_name)
        
        blob.upload_from_filename(file_path)
        blob.make_public()
        
        return blob.public_url
    
    def delete_pdf(self, user_id: str, material_id: str) -> bool:
        """Delete PDF from Firebase Storage"""
        blob_name = f"study_materials/{user_id}/{material_id}.pdf"
        blob = self.bucket.blob(blob_name)
        
        try:
            blob.delete()
            return True
        except Exception as e:
            print(f"Error deleting PDF: {e}")
            return False
    
    # ==================== FIRESTORE OPERATIONS ====================
    
    def save_study_plan(
        self,
        user_id: str,
        material_id: str,
        study_plan_data: Dict[str, Any]
    ) -> str:
        """
        Save study plan to Firestore
        
        Args:
            user_id: User ID
            material_id: Material ID
            study_plan_data: {
                'filename': str,
                'subject': str,
                'grade': int,
                'chunks_created': int,
                'topics': List[str],
                'questions': List[Dict],
                'pdf_url': str,
                'created_at': datetime
            }
        
        Returns: Document ID
        """
        doc_ref = self.db.collection('study_plans').document(material_id)
        
        data = {
            'user_id': user_id,
            'material_id': material_id,
            **study_plan_data,
            'created_at': firestore.SERVER_TIMESTAMP,
            'updated_at': firestore.SERVER_TIMESTAMP
        }
        
        doc_ref.set(data)
        return material_id
    
    def get_study_plan(self, material_id: str) -> Optional[Dict[str, Any]]:
        """Get study plan by ID"""
        doc_ref = self.db.collection('study_plans').document(material_id)
        doc = doc_ref.get()
        
        if doc.exists:
            return doc.to_dict()
        return None
    
    def get_user_study_plans(
        self, 
        user_id: str, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get all study plans for a user"""
        docs = (
            self.db.collection('study_plans')
            .where('user_id', '==', user_id)
            .order_by('created_at', direction=firestore.Query.DESCENDING)
            .limit(limit)
            .stream()
        )
        
        return [{'id': doc.id, **doc.to_dict()} for doc in docs]
    
    def save_practice_session(
        self,
        user_id: str,
        material_id: str,
        session_data: Dict[str, Any]
    ) -> str:
        """
        Save practice session results
        
        Args:
            session_data: {
                'questions': List[Dict],
                'answers': Dict,
                'score': float,
                'percentage': float,
                'grade': str,
                'knowledge_gaps': List[str],
                'recommendations': List[str]
            }
        """
        doc_ref = self.db.collection('practice_sessions').document()
        
        data = {
            'user_id': user_id,
            'material_id': material_id,
            **session_data,
            'created_at': firestore.SERVER_TIMESTAMP
        }
        
        doc_ref.set(data)
        return doc_ref.id
    
    def get_user_progress(self, user_id: str) -> Dict[str, Any]:
        """Get user's overall progress statistics"""
        sessions = (
            self.db.collection('practice_sessions')
            .where('user_id', '==', user_id)
            .stream()
        )
        
        total_sessions = 0
        total_score = 0
        subjects = {}
        
        for session in sessions:
            data = session.to_dict()
            total_sessions += 1
            total_score += data.get('percentage', 0)
            
            subject = data.get('subject', 'Unknown')
            if subject not in subjects:
                subjects[subject] = {'count': 0, 'avg_score': 0}
            subjects[subject]['count'] += 1
            subjects[subject]['avg_score'] += data.get('percentage', 0)
        
        # Calculate averages
        for subject in subjects:
            subjects[subject]['avg_score'] /= subjects[subject]['count']
        
        return {
            'total_sessions': total_sessions,
            'average_score': total_score / total_sessions if total_sessions > 0 else 0,
            'subjects': subjects
        }
    
    def delete_study_plan(self, material_id: str, user_id: str) -> bool:
        """Delete study plan and associated data"""
        try:
            # Delete from Firestore
            self.db.collection('study_plans').document(material_id).delete()
            
            # Delete PDF from Storage
            self.delete_pdf(user_id, material_id)
            
            # Delete associated practice sessions
            sessions = (
                self.db.collection('practice_sessions')
                .where('material_id', '==', material_id)
                .stream()
            )
            for session in sessions:
                session.reference.delete()
            
            return True
        except Exception as e:
            print(f"Error deleting study plan: {e}")
            return False


# Global Firebase service instance
firebase_service = FirebaseService()
```

---

### 3.2 Update Workflow Endpoint

Update `backend/app/api/endpoints/homework_agents.py`:

```python
from app.services.firebase_service import firebase_service

@router.post("/workflow/material-to-practice")
async def material_to_practice_workflow(
    file: UploadFile = File(...),
    subject: str = Form(...),
    grade: int = Form(...),
    question_count: int = Form(10),
    question_types: str = Form("mcq,short_answer"),
    difficulty: str = Form("medium"),
    user_id: str = Form("guest")
):
    """
    Complete workflow with Firebase persistence
    """
    try:
        # ... existing workflow code ...
        
        # After generating questions, save to Firebase
        material_id = workflow_result['results']['ingestion']['material_id']
        
        # Upload PDF to Firebase Storage
        pdf_url = firebase_service.upload_pdf(
            file_path=temp_file_path,
            user_id=user_id,
            material_id=material_id
        )
        
        # Save study plan to Firestore
        study_plan_data = {
            'filename': file.filename,
            'subject': subject,
            'grade': grade,
            'chunks_created': workflow_result['results']['ingestion']['total_chunks'],
            'topics': workflow_result['results']['ingestion']['topics'],
            'questions': workflow_result['results']['questions']['questions'],
            'pdf_url': pdf_url,
            'index_name': workflow_result['results']['search_index']['index_name']
        }
        
        firebase_service.save_study_plan(
            user_id=user_id,
            material_id=material_id,
            study_plan_data=study_plan_data
        )
        
        # Return response with Firebase URLs
        return {
            **workflow_result['results'],
            'material_id': material_id,
            'pdf_url': pdf_url,
            'persisted': True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

### 3.3 Add Endpoints for Retrieval

```python
@router.get("/study-plans/user/{user_id}")
async def get_user_study_plans(user_id: str, limit: int = 10):
    """Get all study plans for a user"""
    plans = firebase_service.get_user_study_plans(user_id, limit)
    return {"study_plans": plans, "total": len(plans)}

@router.get("/study-plans/{material_id}")
async def get_study_plan(material_id: str):
    """Get specific study plan"""
    plan = firebase_service.get_study_plan(material_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Study plan not found")
    return plan

@router.post("/practice-sessions/save")
async def save_practice_session(
    user_id: str = Form(...),
    material_id: str = Form(...),
    session_data: str = Form(...)  # JSON string
):
    """Save practice session results"""
    import json
    data = json.loads(session_data)
    
    session_id = firebase_service.save_practice_session(
        user_id=user_id,
        material_id=material_id,
        session_data=data
    )
    
    return {"session_id": session_id, "saved": True}

@router.get("/progress/{user_id}")
async def get_user_progress(user_id: str):
    """Get user's overall progress"""
    progress = firebase_service.get_user_progress(user_id)
    return progress
```

---

## 🎨 Step 4: Frontend Integration

### 4.1 Update API Service (`frontend/src/services/api.js`)

```javascript
export const homeworkAPI = {
    // ... existing methods ...
    
    // Get user's study plans
    getUserStudyPlans: (userId, limit = 10) => 
        api.get(`/homework-agents/study-plans/user/${userId}?limit=${limit}`),
    
    // Get specific study plan
    getStudyPlan: (materialId) => 
        api.get(`/homework-agents/study-plans/${materialId}`),
    
    // Save practice session
    savePracticeSession: (userId, materialId, sessionData) => {
        const formData = new FormData();
        formData.append('user_id', userId);
        formData.append('material_id', materialId);
        formData.append('session_data', JSON.stringify(sessionData));
        return api.post('/homework-agents/practice-sessions/save', formData);
    },
    
    // Get user progress
    getUserProgress: (userId) => 
        api.get(`/homework-agents/progress/${userId}`)
};
```

### 4.2 Update StudyMaterialAssistant to Save Results

```javascript
const submitPractice = async () => {
    setLoading(true);
    try {
        // ... existing grading code ...
        
        const gradingResult = response.data;
        
        // Save to Firebase
        await homeworkAPI.savePracticeSession(
            localStorage.getItem('user_id') || 'guest',
            materialId,
            {
                questions: questionsForGrading,
                score: gradingResult.total_score,
                percentage: gradingResult.percentage,
                grade: gradingResult.grade,
                knowledge_gaps: gradingResult.knowledge_gaps,
                recommendations: gradingResult.recommendations,
                subject: subject,
                grade_level: grade
            }
        );
        
        // ... rest of code ...
    } catch (error) {
        console.error('Error:', error);
    }
};
```

---

## 🔐 Step 5: Security Setup

### 5.1 Add Firebase Credentials to .env

```bash
# backend/.env
FIREBASE_CREDENTIALS_PATH=firebase-credentials.json
```

### 5.2 Update .gitignore

```
# Firebase
firebase-credentials.json
```

### 5.3 Set Firebase Rules (in Firebase Console)

**Storage Rules:**
```
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /study_materials/{userId}/{allPaths=**} {
      allow read: if request.auth != null && request.auth.uid == userId;
      allow write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

**Firestore Rules:**
```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /study_plans/{planId} {
      allow read: if request.auth != null;
      allow write: if request.auth != null && 
                     request.resource.data.user_id == request.auth.uid;
    }
    
    match /practice_sessions/{sessionId} {
      allow read: if request.auth != null;
      allow write: if request.auth != null &&
                     request.resource.data.user_id == request.auth.uid;
    }
  }
}
```

---

## 📊 Step 6: Data Structure

### Firestore Collections

**study_plans/**
```json
{
  "material_id": "uuid",
  "user_id": "user123",
  "filename": "math_chapter5.pdf",
  "subject": "Mathematics",
  "grade": 5,
  "chunks_created": 12,
  "topics": ["Fractions", "Decimals"],
  "questions": [...],
  "pdf_url": "https://storage.googleapis.com/...",
  "index_name": "math_chapter5_uuid",
  "created_at": "2024-01-04T12:00:00Z",
  "updated_at": "2024-01-04T12:00:00Z"
}
```

**practice_sessions/**
```json
{
  "user_id": "user123",
  "material_id": "uuid",
  "questions": [...],
  "score": 8.5,
  "percentage": 85,
  "grade": "B",
  "knowledge_gaps": ["Fractions"],
  "recommendations": ["Review pages 3-5"],
  "subject": "Mathematics",
  "grade_level": 5,
  "created_at": "2024-01-04T12:30:00Z"
}
```

---

## 🚀 Step 7: Testing

### Test Firebase Connection
```python
# backend/test_firebase.py
from app.services.firebase_service import firebase_service

# Test upload
url = firebase_service.upload_pdf(
    'test.pdf',
    'test_user',
    'test_material_123'
)
print(f"Uploaded: {url}")

# Test save study plan
firebase_service.save_study_plan(
    'test_user',
    'test_material_123',
    {
        'filename': 'test.pdf',
        'subject': 'Math',
        'grade': 5,
        'chunks_created': 10,
        'topics': ['Test'],
        'questions': []
    }
)
print("Study plan saved!")

# Test retrieve
plan = firebase_service.get_study_plan('test_material_123')
print(f"Retrieved: {plan}")
```

---

## ✅ Benefits

1. **Persistent Storage**: Data survives server restarts
2. **User History**: Students can review past study sessions
3. **Progress Tracking**: Analytics on learning progress
4. **Scalable**: Firebase handles millions of users
5. **Real-time**: Updates sync across devices
6. **Secure**: Built-in authentication and rules

---

## 📝 Next Steps

1. Install Firebase Admin SDK
2. Create Firebase project
3. Download credentials
4. Implement firebase_service.py
5. Update endpoints
6. Test with sample data
7. Deploy!

---

## 💰 Cost Estimate

**Firebase Free Tier (Spark Plan):**
- Storage: 5 GB
- Firestore: 1 GB storage, 50K reads/day
- **Cost: $0/month** for moderate usage

**Paid Tier (Blaze Plan):**
- Pay as you go
- ~$0.026/GB storage
- ~$0.06/100K reads
- **Estimated: $5-20/month** for 1000 active users

---

Would you like me to implement this for you? I can create all the files and set it up! 🚀
