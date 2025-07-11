// Firebase configuration
// Replace with your Firebase project configuration
const firebaseConfig = {
    apiKey: "your-api-key",
    authDomain: "your-project.firebaseapp.com",
    projectId: "your-project-id",
    storageBucket: "your-project.appspot.com",
    messagingSenderId: "123456789",
    appId: "your-app-id"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);

// Initialize Firebase Authentication
const auth = firebase.auth();

// Google Auth Provider
const googleProvider = new firebase.auth.GoogleAuthProvider();
googleProvider.addScope('email');
googleProvider.addScope('profile');

// Firebase Authentication Functions
class FirebaseAuth {
    static async signInWithGoogle() {
        try {
            const result = await auth.signInWithPopup(googleProvider);
            return result.user;
        } catch (error) {
            console.error('Google sign-in error:', error);
            throw error;
        }
    }

    static async signOut() {
        try {
            await auth.signOut();
        } catch (error) {
            console.error('Sign-out error:', error);
            throw error;
        }
    }

    static async getCurrentUser() {
        return new Promise((resolve) => {
            const unsubscribe = auth.onAuthStateChanged((user) => {
                unsubscribe();
                resolve(user);
            });
        });
    }

    static async getIdToken() {
        const user = auth.currentUser;
        if (user) {
            return await user.getIdToken();
        }
        throw new Error('No user is signed in');
    }

    static onAuthStateChanged(callback) {
        return auth.onAuthStateChanged(callback);
    }
}

// Export for use in other scripts
window.FirebaseAuth = FirebaseAuth; 