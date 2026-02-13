# **✅ Prompts & Security Rules Used in the Video** 

**🚀 Project Used in the Video — VaultFlow (Google AI)**

If you want to try the same project used in this video, or start from the same base,  
you can use the VaultFlow project link below.

**🔗 VaultFlow Project Link: [Click Here](https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%221P-lytf__6kOkQnOcczVdgIbnOWuRwNF0%22%5D,%22action%22:%22open%22,%22userId%22:%22112386544465239683494%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing)**  
**How to make your own copy:**  
1\. Open the link above.  
2\. Make sure you are logged in to your Google account.  
3\. Click the "Copy" button inside Google AI.  
4\. The project will be copied to your account and becomes fully editable.

You can now modify, experiment, and build on top of it freely.  
**Note:** You’ll need to connect your own Firebase / API keys after copying.

### **Prompt 1 — Connect Firebase Authentication**

**Purpose:**  
 **Connect the Google AI Studio project to Firebase using the Web SDK config \+ enable Sign Up, Login, Logout.**

Connect my existing web app to Firebase using this SDK:  
\[PASTE firebaseConfig HERE\]  
Requirements:  
\- Use Firebase Authentication only  
\- Do NOT use Firestore or Storage yet  
\- Do NOT redesign the UI  
Authentication behavior:  
\- Users can sign in using email and password  
\- If credentials are incorrect, show:  
  "Email or password is incorrect"  
\- Users can sign up using email and password  
\- If the email already exists, show:  
  "User already exists. Please sign in"  
\- For now:  
  \- Authenticate users only  
  \- Do NOT save user profile data  
Flow:  
\- On successful sign-in or sign-up, redirect to the dashboard  
\- Add a logout button that signs the user out and returns to the auth screen  
---

### **Prompt 2 — Implement Email Verification**

**Purpose:**  
 **Enable email verification flow (no auto-login, block unverified users, show verification screen).**

Implement email verification using Firebase Authentication only.  
\- When a user registers with email/password, do not sign them in automatically.  
\- Send a verification email and show a verification screen with this message: “We have sent you a verification email to \[user email\]. Please verify it and log in.”  
\- Include a Login button on the verification screen.  
\- If a user logs in and their email is not verified, block access and show the same verification screen.  
\- Do not use Firestore or any database — Firebase Authentication only.

---

### **Prompt 3 — Add Firestore Dashboard Sections**

**Purpose:**  
 **Add “My Files”, “My Notes”, and “Team Members” sections and store all data in Firestore under the user.**

Enhance the current dashboard by adding 3 fully functional sections:  
1\) My Files  
2\) My Notes  
3\) Team Members

IMPORTANT RULES:  
\- Use Firebase Authentication \+ Firestore only.  
\- Do NOT use browser prompts (window.prompt / alert).  
\- Use clean in-app modals for all actions.  
\- Each user sees ONLY their own data.  
\- Keep the existing VaultFlow UI style (cards, spacing, buttons).

\====================  
DATA STRUCTURE  
\====================

Use Firestore under the authenticated user:

users/{uid}  
\- displayName  
\- email  
\- plan  
\- createdAt

users/{uid}/folders/{folderId}  
\- name  
\- createdAt

users/{uid}/files/{fileId}  
\- name  
\- folderId (optional)  
\- size  
\- createdAt  
(Note: metadata only, no real uploads yet)

users/{uid}/notes/{noteId}  
\- title  
\- content (optional)  
\- createdAt

users/{uid}/teamMembers/{memberId}  
\- name  
\- role (optional)  
\- createdAt

\====================  
UI BEHAVIOR  
\====================

My Files  
\- Buttons: "New Folder" and "Add File"  
\- Show folders and files  
\- Empty state \+ loading state

My Notes  
\- Button: "New Note"  
\- Show notes as cards  
\- Empty state \+ loading state

Team Members  
\- Button: "Add Member"  
\- Show list of members  
\- Empty state \+ loading state

\====================  
MODALS (NO BROWSER PROMPTS)  
\====================

\- New Folder: input name → save to Firestore  
\- Add File: name \+ optional folder \+ size → save  
\- New Note: title \+ content → save  
\- Add Member: name \+ role → save

All modals:  
\- Cancel / Create  
\- Validation  
\- Loading state  
\- Update UI instantly after save

\====================  
SECURITY  
\====================

Add Firestore rules so:  
\- Only the logged-in user can read/write their own data  
\- request.auth.uid must match {uid}

\====================  
RESULT  
\====================

After refresh:  
\- Data persists  
\- Buttons work  
\- Counts update  
\- No browser dialogs  
\- Dashboard feels like a real SaaS app

---

### **Prompt 4 — Connect My Files to Firebase Storage**

**Purpose:**  
 **Enable real file uploads, downloads, and deletion using Firebase Storage \+ Firestore metadata.**

Connect the existing “My Files” section to Firebase Storage \+ Firestore.

CONTEXT  
\- Firebase Auth \+ Firestore already work in this project.  
\- Firebase Storage is enabled.  
\- Storage rules allow only:  
  /user\_uploads/{uid}/{allPaths=\*\*}  for the logged-in user.

GOAL  
Make these buttons fully functional:  
1\) Add File (upload)  
2\) Download  
3\) Delete  
And keep the current UI style (table, buttons, spacing). No redesign.

IMPORTANT RULES  
\- Use Firebase Authentication \+ Firestore \+ Firebase Storage only.  
\- Do NOT use browser prompts (window.prompt/alert).  
\- Use clean in-app modal for “Add File”.  
\- Each user sees ONLY their own files.  
\- Upload path MUST be:  
  user\_uploads/{uid}/{fileName}  
\- Save metadata in Firestore under:  
  users/{uid}/files/{fileId}

UI BEHAVIOR  
A) Add File button  
\- Open an in-app modal: “Upload File”  
\- Inside modal:  
  \- File picker (click to choose file) using a hidden \<input type="file"\>  
  \- Optional: select folder (if folders exist)  
  \- Upload button  
  \- Show upload progress (percentage) \+ loading state  
\- When upload finishes:  
  \- Save metadata doc to Firestore:  
    users/{uid}/files/{fileId} with:  
      \- name (original file name)  
      \- storagePath (e.g. user\_uploads/{uid}/{fileId}-{name})  
      \- downloadURL  
      \- size  
      \- type (mimeType)  
      \- folderId (optional)  
      \- createdAt (serverTimestamp)  
  \- Update the UI immediately (add row in the table)

B) Display files  
\- In “My Files” table, show:  
  \- name  
  \- type  
  \- size  
  \- actions: Download \+ Delete  
\- Use the Firestore list under users/{uid}/files ordered by createdAt desc.

C) Download button  
\- Use the stored downloadURL from Firestore  
\- Open it safely in a new tab OR trigger download (but no alert).

D) Delete button  
\- Delete from Storage using storagePath  
\- Then delete the Firestore document  
\- Update UI instantly

EDGE CASES  
\- If user is not logged in, block access.  
\- Handle errors with inline UI message in the modal (no alerts).  
\- Prevent double uploads (disable button during upload).  
\- If upload fails, show error message.

DELIVERABLE  
\- Implement the missing handlers, modal, and Storage/Firestore logic.  
\- Keep current design. Do not refactor unrelated code.

---

### **Prompt 5 — Add Free Plan File Limit (5 Files)**

**Purpose:**  
 **Disable the Add File button when user reaches 5 files and show an Upgrade message.**

Add a free-plan limit to this app:

• Max files allowed: 5  
• Count files under: users/{uid}/files  
• If file count \>= 5:  
– Disable Add File  
– Show message: “You’ve reached the free plan limit.”  
– Add an Upgrade button that opens a simple modal  
(title: “Upgrade your plan”, text \+ Close button)

No real payments.  
UI only.  
Keep current design.  
Apply logic only to the logged-in user.

### **Security Rules**

1. **Firestore Security Rules (Per-User Data Isolation)**

rules\_version \= '2';

service cloud.firestore {

  match /databases/{database}/documents {

    // Root user document

    match /users/{userId} {

      allow read, write: if request.auth \!= null && request.auth.uid \== userId;

      // Anything nested inside this user:

      // subcollections, documents, folders, files, unlimited levels

      match /{allPaths=\*\*} {

        allow read, write: if request.auth \!= null && request.auth.uid \== userId;

      }

    }

  }

}

2. **Firebase Storage Security Rules (Per-User File Isolation)**

rules\_version \= '2';

service firebase.storage {  
  match /b/{bucket}/o {  
    match /user\_uploads/{uid}/{allPaths=\*\*} {  
      allow read, write: if request.auth \!= null && request.auth.uid \== uid;  
    }  
  }  
}  
