'use client';

import { QRCode } from '@/lib/api';
import { downloadImage, formatDate } from '@/lib/utils';

interface QRCodeDisplayProps {
    qrCode: QRCode;
}

export default function QRCodeDisplay({ qrCode }: QRCodeDisplayProps) {
    const handleDownload = () => {
        const filename = `qrcode-${qrCode.id}-${Date.now()}.png`;
        downloadImage(qrCode.qr_code_image, filename);
    };

    return (
        <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-8 border border-gray-700 shadow-2xl">
            <div className="text-center space-y-6">
                <div className="inline-block p-6 bg-white rounded-xl shadow-lg">
                    <img
                        src={qrCode.qr_code_image}
                        alt={qrCode.title || 'QR Code'}
                        className="w-64 h-64 object-contain"
                    />
                </div>

                <div className="space-y-3">
                    {qrCode.title && (
                        <h3 className="text-2xl font-bold text-white">{qrCode.title}</h3>
                    )}

                    <div className="flex items-center justify-center space-x-2 text-gray-400">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                        </svg>
                        <a
                            href={qrCode.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-purple-400 hover:text-purple-300 transition-colors break-all"
                        >
                            {qrCode.url}
                        </a>
                    </div>

                    {qrCode.description && (
                        <p className="text-gray-400 text-sm">{qrCode.description}</p>
                    )}

                    <div className="flex items-center justify-center space-x-4 text-sm text-gray-500">
                        <span className="flex items-center">
                            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                            </svg>
                            {qrCode.scans} scans
                        </span>
                        <span>•</span>
                        <span>{formatDate(qrCode.created_at)}</span>
                    </div>
                </div>

                <button
                    onClick={handleDownload}
                    className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white font-medium rounded-lg hover:from-green-700 hover:to-emerald-700 focus:ring-2 focus:ring-green-500 focus:ring-offset-2 focus:ring-offset-gray-900 transition-all transform hover:scale-105 active:scale-95"
                >
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                    Download QR Code
                </button>
            </div>
        </div>
    );
}
