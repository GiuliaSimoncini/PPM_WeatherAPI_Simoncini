/**
 * Weather Forecast App Utilities
 * Contains common functions for authentication, API requests, and UI interactions
 */

// Function to show messages to the user
function showMessage(message, isError = false) {
    // Check if message container exists, if not create it
    let messageContainer = document.getElementById('message-container');
    if (!messageContainer) {
        messageContainer = document.createElement('div');
        messageContainer.id = 'message-container';
        messageContainer.style.position = 'fixed';
        messageContainer.style.top = '20px';
        messageContainer.style.left = '50%';
        messageContainer.style.transform = 'translateX(-50%)';
        messageContainer.style.padding = '15px 20px';
        messageContainer.style.borderRadius = '5px';
        messageContainer.style.zIndex = '1000';
        messageContainer.style.boxShadow = '0 4px 8px rgba(0,0,0,0.2)';
        document.body.appendChild(messageContainer);
    }
    
    // Set message style based on type
    messageContainer.style.backgroundColor = isError ? '#f8d7da' : '#d4edda';
    messageContainer.style.color = isError ? '#721c24' : '#155724';
    messageContainer.style.border = isError ? '1px solid #f5c6cb' : '1px solid #c3e6cb';
    
    // Set message content
    messageContainer.textContent = message;
    
    // Show the message
    messageContainer.style.display = 'block';
    
    // Hide message after 5 seconds
    setTimeout(() => {
        messageContainer.style.display = 'none';
    }, 5000);
}

// Function to check if user is authenticated
function isAuthenticated() {
    return localStorage.getItem('token') !== null;
}

// Function to get the authentication token
function getToken() {
    return localStorage.getItem('token');
}

// Function to get the current username
function getUsername() {
    return localStorage.getItem('username');
}

// Function to logout user
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    window.location.href = '/login/';
}

// Function to make authenticated API requests
async function apiRequest(url, method = 'GET', data = null) {
    const token = getToken();
    
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    // Add authorization header if token exists
    if (token) {
        options.headers['Authorization'] = `Bearer ${token}`;
    }
    
    // Add request body for POST, PUT methods
    if (data && (method === 'POST' || method === 'PUT')) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(url, options);
        
        // Handle unauthorized responses (expired token)
        if (response.status === 401) {
            logout();
            throw new Error('Session expired. Please login again.');
        }
        
        // Parse JSON response
        const responseData = await response.json();
        
        // If response is not ok, throw error
        if (!response.ok) {
            throw new Error(JSON.stringify(responseData));
        }
        
        return responseData;
    } catch (error) {
        console.error('API Request Error:', error);
        throw error;
    }
}