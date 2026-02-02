from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from app.database import Base

class QRCode(Base):
    """QRCode model for storing QR code information"""
    __tablename__ = "qrcodes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=True)
    url = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    qr_code_image = Column(Text, nullable=False)  # Base64 encoded image
    created_at = Column(DateTime, default=datetime.utcnow)
    scans = Column(Integer, default=0)  # Track usage

    def __repr__(self):
        return f"<QRCode(id={self.id}, title={self.title}, url={self.url})>"
