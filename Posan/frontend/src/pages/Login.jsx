import React, { useEffect } from 'react';
import { useKeycloak } from '@react-keycloak/web';
import { Navigate } from 'react-router-dom';

const Login = () => {
    const { keycloak, initialized } = useKeycloak();

    useEffect(() => {
        if (initialized && !keycloak.authenticated) {
            keycloak.login();
        }
    }, [initialized, keycloak]);

    if (keycloak.authenticated) {
        return <Navigate to="/" />;
    }

    return (
        <div className="loading-screen" style={{ height: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
            <div style={{ textAlign: 'center' }}>
                <div className="spinner" style={{ marginBottom: '1rem' }}></div>
                <p>Redirecting to secure login...</p>
            </div>
        </div>
    );
};

export default Login;
