# secrets/

This folder holds local credentials that must never be committed. Everything
in here except this file is gitignored (`secrets/*` with `!secrets/README.md`).

## Firebase service account key

`src/tools/firebase_ops.py` needs a Firebase **service account** JSON key to
write to Firestore as an admin (bypassing security rules). To get one:

1. [Firebase console](https://console.firebase.google.com/) → create a demo
   project (e.g. `company-brain-demo`) — not a real client's project.
2. **Build → Firestore Database → Create database** (any mode/location; the
   service account bypasses security rules, so the mode you pick here
   doesn't matter for this agent).
3. **Project settings (gear icon) → Service accounts → Generate new private
   key**. This downloads a JSON file.
4. Save it here as `secrets/firebase-service-account.json`.

The default path `firebase-ops.py` looks for is
`secrets/firebase-service-account.json`. Override it by setting the
`FIREBASE_SERVICE_ACCOUNT_PATH` environment variable instead, if you'd
rather keep the key elsewhere.
