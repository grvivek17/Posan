import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './styles/global.css';
import './styles/animations.css';

// Pages
import Home from './pages/Home';
import About from './pages/About';
import Login from './pages/Login';
import Register from './pages/Register';
import MagazinePage from './pages/MagazinePage';
import MagazineDetailPage from './pages/MagazineDetailPage';
import PuzzlePage from './pages/PuzzlePage';
import ProfilePage from './pages/ProfilePage';
import ParentPortal from './pages/ParentPortal';
import AIContentPage from './pages/AIContentPage';
import PuzzleZone from './pages/PuzzleZone';
import HomeworkPage from './pages/HomeworkPage';

// Components
import Header from './components/common/Header';
import Footer from './components/common/Footer';

function App() {
    const [isAuthenticated, setIsAuthenticated] = React.useState(false);

    React.useEffect(() => {
        // Check if user is authenticated
        const token = localStorage.getItem('access_token');
        setIsAuthenticated(!!token);
    }, []);

    return (
        <Router>
            <div className="app">
                <Header isAuthenticated={isAuthenticated} setIsAuthenticated={setIsAuthenticated} />
                <main className="main-content">
                    <Routes>
                        <Route path="/" element={<Home />} />
                        <Route path="/about" element={<About />} />
                        <Route path="/login" element={<Login setIsAuthenticated={setIsAuthenticated} />} />
                        <Route path="/register" element={<Register setIsAuthenticated={setIsAuthenticated} />} />
                        <Route
                            path="/magazines"
                            element={isAuthenticated ? <MagazinePage /> : <Navigate to="/login" />}
                        />
                        <Route
                            path="/magazines/:id"
                            element={isAuthenticated ? <MagazineDetailPage /> : <Navigate to="/login" />}
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
                            path="/homework"
                            element={isAuthenticated ? <HomeworkPage /> : <Navigate to="/login" />}
                        />
                    </Routes>
                </main>
                <Footer />
            </div>
        </Router>
    );
}

export default App;
