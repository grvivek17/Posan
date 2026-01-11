"""
Firebase Service for Study Plan Persistence

This service handles:
- Uploading PDFs to Firebase Storage
- Saving study plans to Firestore
- Saving practice session results
- Retrieving user's study history and progress
"""
import firebase_admin
from firebase_admin import credentials, storage, firestore
from typing import Dict, Any, Optional, List
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)


class FirebaseService:
    """Service for Firebase Storage and Firestore operations"""
    
    def __init__(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Get credentials path from environment
            cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')
            
            # Initialize Firebase if not already initialized
            if not firebase_admin._apps:
                if os.path.exists(cred_path):
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred, {
                        'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET', 'posan-study-assistant.appspot.com')
                    })
                    logger.info("✅ Firebase initialized successfully")
                else:
                    logger.warning(f"⚠️  Firebase credentials not found at {cred_path}")
                    logger.warning("Firebase features will be disabled")
                    self.enabled = False
                    return
            
            self.db = firestore.client()
            self.bucket = storage.bucket()
            self.enabled = True
            
        except Exception as e:
            logger.error(f"❌ Firebase initialization failed: {e}")
            self.enabled = False
    
    def is_enabled(self) -> bool:
        """Check if Firebase is enabled"""
        return self.enabled
    
    # ==================== STORAGE OPERATIONS ====================
    
    def upload_pdf(
        self, 
        file_path: str, 
        user_id: str, 
        material_id: str
    ) -> Optional[str]:
        """
        Upload PDF to Firebase Storage
        
        Args:
            file_path: Local path to PDF file
            user_id: User ID
            material_id: Unique material ID
        
        Returns: Public URL of uploaded file, or None if disabled
        """
        if not self.enabled:
            logger.warning("Firebase is disabled, skipping PDF upload")
            return None
        
        try:
            blob_name = f"study_materials/{user_id}/{material_id}.pdf"
            blob = self.bucket.blob(blob_name)
            
            blob.upload_from_filename(file_path)
            blob.make_public()
            
            logger.info(f"✅ PDF uploaded: {blob_name}")
            return blob.public_url
            
        except Exception as e:
            logger.error(f"❌ PDF upload failed: {e}")
            return None
    
    def delete_pdf(self, user_id: str, material_id: str) -> bool:
        """Delete PDF from Firebase Storage"""
        if not self.enabled:
            return False
        
        try:
            blob_name = f"study_materials/{user_id}/{material_id}.pdf"
            blob = self.bucket.blob(blob_name)
            blob.delete()
            
            logger.info(f"✅ PDF deleted: {blob_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ PDF deletion failed: {e}")
            return False
    
    # ==================== FIRESTORE OPERATIONS ====================
    
    def save_study_plan(
        self,
        user_id: str,
        material_id: str,
        study_plan_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Save study plan to Firestore
        
        Args:
            user_id: User ID
            material_id: Material ID
            study_plan_data: Dictionary containing:
                - filename: str
                - subject: str
                - grade: int
                - chunks_created: int
                - topics: List[str]
                - questions: List[Dict]
                - pdf_url: str (optional)
                - index_name: str
        
        Returns: Document ID or None if disabled
        """
        if not self.enabled:
            logger.warning("Firebase is disabled, skipping study plan save")
            return None
        
        try:
            doc_ref = self.db.collection('study_plans').document(material_id)
            
            data = {
                'user_id': user_id,
                'material_id': material_id,
                **study_plan_data,
                'created_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP
            }
            
            doc_ref.set(data)
            logger.info(f"✅ Study plan saved: {material_id}")
            return material_id
            
        except Exception as e:
            logger.error(f"❌ Study plan save failed: {e}")
            return None
    
    def get_study_plan(self, material_id: str) -> Optional[Dict[str, Any]]:
        """Get study plan by ID"""
        if not self.enabled:
            return None
        
        try:
            doc_ref = self.db.collection('study_plans').document(material_id)
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            return None
            
        except Exception as e:
            logger.error(f"❌ Study plan retrieval failed: {e}")
            return None
    
    def get_user_study_plans(
        self, 
        user_id: str, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get all study plans for a user"""
        if not self.enabled:
            return []
        
        try:
            docs = (
                self.db.collection('study_plans')
                .where('user_id', '==', user_id)
                .order_by('created_at', direction=firestore.Query.DESCENDING)
                .limit(limit)
                .stream()
            )
            
            plans = [{'id': doc.id, **doc.to_dict()} for doc in docs]
            logger.info(f"✅ Retrieved {len(plans)} study plans for user {user_id}")
            return plans
            
        except Exception as e:
            logger.error(f"❌ Study plans retrieval failed: {e}")
            return []
    
    def save_practice_session(
        self,
        user_id: str,
        material_id: str,
        session_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Save practice session results
        
        Args:
            user_id: User ID
            material_id: Material ID
            session_data: Dictionary containing:
                - questions: List[Dict]
                - score: float
                - percentage: float
                - grade: str
                - knowledge_gaps: List[str]
                - recommendations: List[str]
                - subject: str
                - grade_level: int
        
        Returns: Session ID or None if disabled
        """
        if not self.enabled:
            logger.warning("Firebase is disabled, skipping session save")
            return None
        
        try:
            doc_ref = self.db.collection('practice_sessions').document()
            
            data = {
                'user_id': user_id,
                'material_id': material_id,
                **session_data,
                'created_at': firestore.SERVER_TIMESTAMP
            }
            
            doc_ref.set(data)
            logger.info(f"✅ Practice session saved: {doc_ref.id}")
            return doc_ref.id
            
        except Exception as e:
            logger.error(f"❌ Practice session save failed: {e}")
            return None
    
    def get_user_progress(self, user_id: str) -> Dict[str, Any]:
        """Get user's overall progress statistics"""
        if not self.enabled:
            return {
                'total_sessions': 0,
                'average_score': 0,
                'subjects': {}
            }
        
        try:
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
                    subjects[subject] = {'count': 0, 'total_score': 0}
                subjects[subject]['count'] += 1
                subjects[subject]['total_score'] += data.get('percentage', 0)
            
            # Calculate averages
            for subject in subjects:
                subjects[subject]['avg_score'] = subjects[subject]['total_score'] / subjects[subject]['count']
                del subjects[subject]['total_score']
            
            return {
                'total_sessions': total_sessions,
                'average_score': total_score / total_sessions if total_sessions > 0 else 0,
                'subjects': subjects
            }
            
        except Exception as e:
            logger.error(f"❌ Progress retrieval failed: {e}")
            return {
                'total_sessions': 0,
                'average_score': 0,
                'subjects': {}
            }
    
    def delete_study_plan(self, material_id: str, user_id: str) -> bool:
        """Delete study plan and associated data"""
        if not self.enabled:
            return False
        
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
            
            logger.info(f"✅ Study plan deleted: {material_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Study plan deletion failed: {e}")
            return False


# Global Firebase service instance
firebase_service = FirebaseService()
