/*
  Firebase client SDK initialisation.

  NOT wired into the app yet — nothing imports this file. It exists so the
  moment a real Firebase project's config is available (as environment
  variables, see .env.example), Phase 0 of FIREBASE_INTEGRATION_GUIDE.md
  is "set the env vars and start importing this," not "write this file."

  All config values below are read from NEXT_PUBLIC_* environment
  variables — nothing is hard-coded, and nothing here is a secret (the
  Firebase Web SDK config is designed to be public; Security Rules,
  defined in firestore.rules/storage.rules, are what actually protect
  data — see DATA_MODEL.md).

  If the required env vars aren't set (e.g. local dev before Phase 0
  starts), initialisation is skipped rather than throwing, so the rest of
  the app — which doesn't depend on this yet — keeps working normally.
*/

import { initializeApp, getApps, getApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';
import { getStorage } from 'firebase/storage';

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
};

const isConfigured = Boolean(firebaseConfig.apiKey && firebaseConfig.projectId);

function getFirebaseApp() {
  if (!isConfigured) {
    throw new Error(
      'Firebase is not configured. Set the NEXT_PUBLIC_FIREBASE_* environment variables ' +
        '(see .env.example) before calling any Firebase-backed service function. ' +
        'See FIREBASE_INTEGRATION_GUIDE.md Phase 0.'
    );
  }
  return getApps().length ? getApp() : initializeApp(firebaseConfig);
}

// Lazy accessors, not top-level singletons — calling initializeApp() at
// module load time would throw on import in every environment that
// doesn't have Firebase configured yet (i.e. everywhere, today). A
// service function calls these only once it actually needs Firebase,
// at which point a clear, actionable error is the right failure mode if
// the env vars are still missing.
export function firebaseAuth() {
  return getAuth(getFirebaseApp());
}

export function firestoreDb() {
  return getFirestore(getFirebaseApp());
}

export function firebaseStorage() {
  return getStorage(getFirebaseApp());
}

export { isConfigured as isFirebaseConfigured };
