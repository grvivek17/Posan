import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './styles/global.css';
import './styles/animations.css';

// Auto-redirect from legacy Vercel domain to self-hosted server
if (typeof window !== 'undefined' && window.location.hostname.includes('vercel.app')) {
    window.location.replace('http://129.225.82.229/magazines');
}

// Pages
import Home from './pages/Home';
import About from './pages/About';
import Login from './pages/Login';
import Register from './pages/Register';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
import MagazinePage from './pages/MagazinePage';
import MagazineDetailPage from './pages/MagazineDetailPage';
import PuzzlePage from './pages/PuzzlePage';
import ProfilePage from './pages/ProfilePage';
import ParentPortal from './pages/ParentPortal';
import AIContentPage from './pages/AIContentPage';
import PuzzleZone from './pages/PuzzleZone';
import HomeworkPage from './pages/HomeworkPage';
import GamificationPage from './pages/GamificationPage';
import TestSubscriptionPage from './pages/TestSubscriptionPage';
import AdminDashboard from './pages/AdminDashboard';
import AdminUsersPage from './pages/AdminUsersPage';
import AdminUserDetailPage from './pages/AdminUserDetailPage';
import AdminSubscriptionsPage from './pages/AdminSubscriptionsPage';
import ActivityBookStore from './pages/ActivityBookStore';
import CheckoutPage from './pages/CheckoutPage';
import AdminProductsPage from './pages/AdminProductsPage';
import OrderHistoryPage from './pages/OrderHistoryPage';
import AdminOrdersPage from './pages/AdminOrdersPage';
import AdminPromotionalEmailPage from './pages/AdminPromotionalEmailPage';
import PodcastsPage from './pages/PodcastsPage';
import GamesPage from './pages/GamesPage';
// Components
import RunningBanner from './components/common/RunningBanner';
import Header from './components/common/Header';
import Footer from './components/common/Footer';
import ScrollToTop from './components/common/ScrollToTop';
import BottomNav from './components/common/BottomNav';

function App() {
    const [isAuthenticated, setIsAuthenticated] = React.useState(false);

    React.useEffect(() => {
        // Check if user is authenticated
        const token = localStorage.getItem('access_token');
        setIsAuthenticated(!!token);
    }, []);

    return (
        <Router>
            <ScrollToTop />
            <div className="app">
                <RunningBanner />
                <Header isAuthenticated={isAuthenticated} setIsAuthenticated={setIsAuthenticated} />
                <main className="main-content">
                    <Routes>
                        <Route path="/" element={<Home />} />
                        <Route path="/about" element={<About />} />
                        <Route path="/login" element={<Login setIsAuthenticated={setIsAuthenticated} />} />
                        <Route path="/register" element={<Register setIsAuthenticated={setIsAuthenticated} />} />
                        <Route path="/forgot-password" element={<ForgotPassword />} />
                        <Route path="/reset-password" element={<ResetPassword />} />
                        <Route
                            path="/magazines"
                            element={isAuthenticated ? <MagazinePage /> : <Navigate to="/login" />}
                        />
                        <Route
                            path="/magazines/:id"
                            element={isAuthenticated ? <MagazineDetailPage /> : <Navigate to="/login" />}
                        />
                        <Route
                            path="/store"
                            element={<ActivityBookStore />}
                        />
                        <Route
                            path="/store/checkout"
                            element={isAuthenticated ? <CheckoutPage /> : <Navigate to="/login" />}
                        />
                        <Route
                            path="/store/orders"
                            element={isAuthenticated ? <OrderHistoryPage /> : <Navigate to="/login" />}
                        />
                        <Route
                            path="/puzzles"
                            element={isAuthenticated ? <PuzzlePage /> : <Navigate to="/login" />}
                        />
                        <Route
                            path="/profile"
                            element={isAuthenticated ? <ProfilePage /> : <Navigate to="/login" />}
                        />
                        <Route
                            path="/parent"
                            element={isAuthenticated ? <ParentPortal /> : <Navigate to="/login" />}
                        />
                        <Route
                            path="/ai-content"
                            element={isAuthenticated ? <AIContentPage /> : <Navigate to="/login" />}
                        />
                        <Route
                            path="/puzzle-zone"
                            element={isAuthenticated ? <PuzzleZone /> : <Navigate to="/login" />}
                        />
                        <Route
                            path="/games"
                            element={isAuthenticated ? <GamesPage /> : <Navigate to="/login" />}
                        />
                        <Route
                            path="/podcasts"
                            element={isAuthenticated ? <PodcastsPage /> : <Navigate to="/login" />}
                        />
                        <Route
                            path="/homework"
                            element={isAuthenticated ? <HomeworkPage /> : <Navigate to="/login" />}
                        />
                        <Route
                            path="/achievements"
                            element={isAuthenticated ? <GamificationPage /> : <Navigate to="/login" />}
                        />
                        <Route
                            path="/test-subscription"
                            element={isAuthenticated ? <TestSubscriptionPage /> : <Navigate to="/login" />}
                        />
                        {/* Admin Routes */}
                        <Route
                            path="/admin"
                            element={isAuthenticated ? <AdminDashboard /> : <Navigate to="/login" />}
                        />
                        <Route
                            path="/admin/users"
                            element={isAuthenticated ? <AdminUsersPage /> : <Navigate to="/login" />}
                        />
                        <Route
                            path="/admin/users/:id"
                            element={isAuthenticated ? <AdminUserDetailPage /> : <Navigate to="/login" />}
                        />
                        <Route
                            path="/admin/subscriptions"
                            element={isAuthenticated ? <AdminSubscriptionsPage /> : <Navigate to="/login" />}
                        />
                        <Route
                            path="/admin/products"
                            element={isAuthenticated ? <AdminProductsPage /> : <Navigate to="/login" />}
                        />
                        <Route
                            path="/admin/orders"
                            element={isAuthenticated ? <AdminOrdersPage /> : <Navigate to="/login" />}
                        />
                        <Route
                            path="/admin/promotional-email"
                            element={isAuthenticated ? <AdminPromotionalEmailPage /> : <Navigate to="/login" />}
                        />
                    </Routes>
                </main>
                <Footer />
                {isAuthenticated && <BottomNav />}
            </div>
        </Router>
    );
}

export default App;
