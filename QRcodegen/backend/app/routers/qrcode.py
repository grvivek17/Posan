from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import qrcode
import io
import base64
from app.database import get_db
from app.models import QRCode
from app.schemas import QRCodeCreate, QRCodeResponse, QRCodeList

router = APIRouter(prefix="/api/qrcodes", tags=["QR Codes"])

def generate_qr_code(url: str) -> str:
    """Generate QR code and return base64 encoded image"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"

@router.post("/", response_model=QRCodeResponse, status_code=status.HTTP_201_CREATED)
async def create_qr_code(qr_data: QRCodeCreate, db: Session = Depends(get_db)):
    """Create a new QR code"""
    try:
        # Generate QR code image
        qr_image = generate_qr_code(qr_data.url)
        
        # Create database entry
        db_qr_code = QRCode(
            title=qr_data.title,
            url=qr_data.url,
            description=qr_data.description,
            qr_code_image=qr_image
        )
        
        db.add(db_qr_code)
        db.commit()
        db.refresh(db_qr_code)
        
        return db_qr_code
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create QR code: {str(e)}"
        )

@router.get("/", response_model=List[QRCodeList])
async def get_all_qr_codes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all QR codes"""
    qr_codes = db.query(QRCode).order_by(QRCode.created_at.desc()).offset(skip).limit(limit).all()
    return qr_codes

@router.get("/{qr_code_id}", response_model=QRCodeResponse)
async def get_qr_code(qr_code_id: int, db: Session = Depends(get_db)):
    """Get a specific QR code by ID"""
    qr_code = db.query(QRCode).filter(QRCode.id == qr_code_id).first()
    
    if not qr_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"QR code with ID {qr_code_id} not found"
        )
    
    # Increment scan count
    qr_code.scans += 1
    db.commit()
    
    return qr_code

@router.delete("/{qr_code_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_qr_code(qr_code_id: int, db: Session = Depends(get_db)):
    """Delete a QR code"""
    qr_code = db.query(QRCode).filter(QRCode.id == qr_code_id).first()
    
    if not qr_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"QR code with ID {qr_code_id} not found"
        )
    
    db.delete(qr_code)
    db.commit()
    
    return None
