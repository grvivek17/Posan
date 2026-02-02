'use client';

import { useState } from 'react';
import QRCodeForm from '@/components/QRCodeForm';
import QRCodeDisplay from '@/components/QRCodeDisplay';
import QRCodeGallery from '@/components/QRCodeGallery';
import { QRCode } from '@/lib/api';

export default function Home() {
  const [latestQRCode, setLatestQRCode] = useState<QRCode | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleQRCodeCreated = (qrCode: QRCode) => {
    setLatestQRCode(qrCode);
    setRefreshTrigger(prev => prev + 1);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-gradient-to-br from-purple-600 to-pink-600 rounded-lg">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z" />
                </svg>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">QR Code Generator</h1>
                <p className="text-sm text-gray-400">Create QR codes for your websites instantly</p>
              </div>
            </div>
            <div className="hidden md:flex items-center space-x-2 text-sm text-gray-400">
              <span className="flex items-center">
                <span className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></span>
                API Connected
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid lg:grid-cols-2 gap-8 mb-12">
          {/* Form Section */}
          <div className="space-y-6">
            <div>
              <h2 className="text-3xl font-bold text-white mb-2">Create New QR Code</h2>
              <p className="text-gray-400">Enter a URL to generate a scannable QR code</p>
            </div>

            <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-8 border border-gray-700 shadow-2xl">
              <QRCodeForm onSuccess={handleQRCodeCreated} />
            </div>

            {/* Features */}
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-purple-500/20 rounded-lg">
                    <svg className="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-white">Instant</p>
                    <p className="text-xs text-gray-400">Generate in seconds</p>
                  </div>
                </div>
              </div>

              <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-green-500/20 rounded-lg">
                    <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-white">Download</p>
                    <p className="text-xs text-gray-400">PNG format</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Display Section */}
          <div className="space-y-6">
            <div>
              <h2 className="text-3xl font-bold text-white mb-2">Latest QR Code</h2>
              <p className="text-gray-400">Your most recently created QR code</p>
            </div>

            {latestQRCode ? (
              <QRCodeDisplay qrCode={latestQRCode} />
            ) : (
              <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-12 border border-gray-700 shadow-2xl">
                <div className="text-center space-y-4">
                  <div className="inline-block p-6 bg-gray-800 rounded-full">
                    <svg className="w-16 h-16 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-gray-400">No QR Code Yet</h3>
                    <p className="text-gray-500 mt-2">Generate your first QR code to see it here</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Gallery Section */}
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-3xl font-bold text-white mb-2">All QR Codes</h2>
              <p className="text-gray-400">Browse and manage your QR codes</p>
            </div>
          </div>

          <QRCodeGallery refreshTrigger={refreshTrigger} />
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-800 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-gray-500 text-sm">
            <p>Built with Next.js, FastAPI, and PostgreSQL</p>
            <p className="mt-2">© 2026 QR Code Generator. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
