//firebase setup code 
// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries
import { getFirestore } from "firebase/firestore";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
    apiKey: "AIzaSyCChcCcPF_PNMauFSZrD2SDyqVgdWny9kA",
    authDomain: "scorex-35800.firebaseapp.com",
    projectId: "scorex-35800",
    storageBucket: "scorex-35800.appspot.com",
    messagingSenderId: "511213887827",
    appId: "1:511213887827:web:228548366825f2b37441a6",
    measurementId: "G-JV8FXY5TV8"
  };
  const app = initializeApp(firebaseConfig);
  const analytics = getAnalytics(app);
  const db = getFirestore(app);
  const auth = getAuth(app);

  export {
    app,
    db,
    auth,
    analytics
  };