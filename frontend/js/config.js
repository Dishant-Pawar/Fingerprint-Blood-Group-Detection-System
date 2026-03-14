// API Configuration - Change based on environment
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000'
    : 'https://your-heroku-backend.herokuapp.com';  // Update with your Heroku URL

console.log('API Base URL:', API_BASE_URL);
