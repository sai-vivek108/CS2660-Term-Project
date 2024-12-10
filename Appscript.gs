function syncFirestoreToGoogleSheets() {
    const FIRESTORE_PROJECT_ID = "qrcode-444118"; // Firestore project ID
    const FIRESTORE_COLLECTION = "Sessions"; // Firestore collection name
    const FIRESTORE_API_URL = `https://firestore.googleapis.com/v1/projects/${FIRESTORE_PROJECT_ID}/databases/(default)/documents/`;
  
    const SPREADSHEET_ID = "1uQHbIqnYeF5fJIp-gHxXl73TEsPuTNXOpVwhVGfZJjg"; // Spreadsheet ID
    const SHEET_NAME = "Attendance"; // Sheet tab name
  
    const sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(SHEET_NAME);
  
    sheet.clear(); // Clear existing data
    sheet.appendRow(["Student ID", "Name", "Present", "Timestamp"]); // Add headers
  
    const sessionId = "Session_2024-12-09"; // Example session ID
    const firestoreAuth = getFirestoreAccessToken(); // Call authentication function
  
    const options = {
      headers: {
        Authorization: `Bearer ${firestoreAuth}`
      },
      muteHttpExceptions: true
    };
  
    const response = UrlFetchApp.fetch(FIRESTORE_API_URL + `${FIRESTORE_COLLECTION}/${sessionId}/Attendance`, options);
    const data = JSON.parse(response.getContentText());
  
    if (data.error) {
      Logger.log(`Error fetching data: ${data.error.message}`);
      return;
    }
  
    data.documents.forEach((doc) => {
      const fields = doc.fields;
      sheet.appendRow([
        fields.student_id.stringValue,
        fields.name.stringValue,
        fields.present.booleanValue ? "Yes" : "No",
        fields.timestamp.stringValue || "N/A",
      ]);
    });
  
    Logger.log(`Data for ${sessionId} synced to Google Sheets.`);
  }
  //service account details
  function getFirestoreAccessToken() {
    const serviceAccount = {
      "type": "service_account",
      "project_id": "qrcode-444118",
      "private_key_id": "",
      "private_key": "",
      "client_email": "qrcode-service@qrcode-444118.iam.gserviceaccount.com",
      "client_id": "",
      "auth_uri": "https://accounts.google.com/o/oauth2/auth",
      "token_uri": "https://oauth2.googleapis.com/token",
      "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
      "client_x509_cert_url": "",
      "universe_domain": "googleapis.com"
    };
    const tokenUrl = "https://oauth2.googleapis.com/token";
    const tokenPayload = {
      grant_type: "urn:ietf:params:oauth:grant-type:jwt-bearer",
      assertion: createJwt(serviceAccount)
    };
    const options = {
      method: "post",
      contentType: "application/x-www-form-urlencoded",
      payload: tokenPayload
    };
    const tokenResponse = UrlFetchApp.fetch(tokenUrl, options);
    const tokenData = JSON.parse(tokenResponse.getContentText());
    return tokenData.access_token;
  }
  
  function createJwt(serviceAccount) {
    const header = { alg: "RS256", typ: "JWT" };
    const now = Math.floor(Date.now() / 1000);
    const payload = {
      iss: serviceAccount.client_email,
      scope: "https://www.googleapis.com/auth/datastore",
      aud: "https://oauth2.googleapis.com/token",
      exp: now + 3600,
      iat: now
    };
    const encodedHeader = Utilities.base64EncodeWebSafe(JSON.stringify(header));
    const encodedPayload = Utilities.base64EncodeWebSafe(JSON.stringify(payload));
    const signature = Utilities.computeRsaSha256Signature(
      `${encodedHeader}.${encodedPayload}`,
      serviceAccount.private_key
    );
    const encodedSignature = Utilities.base64EncodeWebSafe(signature);
    return `${encodedHeader}.${encodedPayload}.${encodedSignature}`;
  }
  