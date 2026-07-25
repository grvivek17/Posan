import Keycloak from 'keycloak-js';

const keycloakConfig = {
    url: import.meta.env.VITE_KEYCLOAK_URL || 'http://localhost:8080', // Replace with your Keycloak URL
    realm: import.meta.env.VITE_KEYCLOAK_REALM || 'posan-realm',
    clientId: import.meta.env.VITE_KEYCLOAK_CLIENT_ID || 'posan-frontend-client'
};

const keycloak = new Keycloak(keycloakConfig);

export default keycloak;
