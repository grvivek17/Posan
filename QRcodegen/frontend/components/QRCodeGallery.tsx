'use client';

import { useEffect, useState } from 'react';
import { qrCodeApi, QRCode } from '@/lib/api';
import { formatDate, downloadImage } from '@/lib/utils';

interface QRCodeGalleryProps {
    refreshTrigger?: number;
}

export default function QRCodeGallery({ refreshTrigger }: QRCodeGalleryProps) {
    const [qrCodes, setQrCodes] = useState<QRCode[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchQRCodes = async () => {
        try {
            setLoading(true);
            setError(null);
            const codes = await qrCodeApi.getAllQRCodes();
            setQrCodes(codes);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch QR codes');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchQRCodes();
    }, [refreshTrigger]);

    const handleDelete = async (id: number) => {
        if (!confirm('Are you sure you want to delete this QR code?')) {
            return;
        }

        try {
            await qrCodeApi.deleteQRCode(id);
            setQrCodes(qrCodes.filter(qr => qr.id !== id));
        } catch (err) {
            alert('Failed to delete QR code');
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-4 bg-red-500/10 border border-red-500/50 rounded-lg text-red-400">
                {error}
            </div>
        );
    }

    if (qrCodes.length === 0) {
        return (
            <div className="text-center py-12">
                <svg className="mx-auto h-12 w-12 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                </svg>
                <h3 className="mt-2 text-lg font-medium text-gray-400">No QR codes yet</h3>
                <p className="mt-1 text-sm text-gray-500">Get started by creating your first QR code above.</p>
            </div>
        );
    }

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {qrCodes.map((qrCode) => (
                <div
                    key={qrCode.id}
                    className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-6 border border-gray-700 hover:border-purple-500 transition-all duration-300 transform hover:scale-105 group"
                >
                    <div className="space-y-4">
                        <div className="bg-white rounded-lg p-4 inline-block">
                            <img
                                src={qrCode.qr_code_image}
                                alt={qrCode.title || 'QR Code'}
                                className="w-32 h-32 object-contain mx-auto"
                            />
                        </div>

                        <div className="space-y-2">
                            {qrCode.title && (
                                <h4 className="font-semibold text-white text-lg truncate">{qrCode.title}</h4>
                            )}

                            <a
                                href={qrCode.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-purple-400 hover:text-purple-300 text-sm truncate block transition-colors"
                            >
                                {qrCode.url}
                            </a>

                            {qrCode.description && (
                                <p className="text-gray-400 text-sm line-clamp-2">{qrCode.description}</p>
                            )}

                            <div className="flex items-center justify-between text-xs text-gray-500 pt-2">
                                <span className="flex items-center">
                                    <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                    </svg>
                                    {qrCode.scans} scans
                                </span>
                                <span>{new Date(qrCode.created_at).toLocaleDateString()}</span>
                            </div>
                        </div>

                        <div className="flex space-x-2 pt-2">
                            <button
                                onClick={() => downloadImage(qrCode.qr_code_image, `qrcode-${qrCode.id}.png`)}
                                className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-lg transition-colors flex items-center justify-center"
                            >
                                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                                </svg>
                                Download
                            </button>
                            <button
                                onClick={() => handleDelete(qrCode.id)}
                                className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-lg transition-colors"
                            >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                </svg>
                            </button>
                        </div>
                    </div>
                </div>
            ))}
        </div>
    );
}
