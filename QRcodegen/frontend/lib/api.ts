const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface QRCode {
  id: number;
  title?: string;
  url: string;
  description?: string;
  qr_code_image: string;
  created_at: string;
  scans: number;
}

export interface CreateQRCodeData {
  title?: string;
  url: string;
  description?: string;
}

export const qrCodeApi = {
  async createQRCode(data: CreateQRCodeData): Promise<QRCode> {
    const response = await fetch(`${API_URL}/api/qrcodes/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create QR code');
    }

    return response.json();
  },

  async getAllQRCodes(): Promise<QRCode[]> {
    const response = await fetch(`${API_URL}/api/qrcodes/`);

    if (!response.ok) {
      throw new Error('Failed to fetch QR codes');
    }

    return response.json();
  },

  async getQRCode(id: number): Promise<QRCode> {
    const response = await fetch(`${API_URL}/api/qrcodes/${id}`);

    if (!response.ok) {
      throw new Error('Failed to fetch QR code');
    }

    return response.json();
  },

  async deleteQRCode(id: number): Promise<void> {
    const response = await fetch(`${API_URL}/api/qrcodes/${id}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error('Failed to delete QR code');
    }
  },
};
