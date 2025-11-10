import smtplib
import ssl

# --- Your Brevo Credentials ---
# ⚠️ IMPORTANT: Replace with your actual credentials
smtp_server = "smtp-relay.brevo.com"
port = 587
sender_email = "9931bc002@smtp-brevo.com"  # Your Brevo login email
password = "pr6vSaPDzEA357Kw"             # Your Brevo SMTP Key
receiver_email = "sharonzane790@gmail.com" # Where to send the test email

# --- The Email Message ---
subject = "Direct Python SMTP Test"
body = "This is a test email sent directly from a Python script to check the Brevo connection."
message = f"Subject: {subject}\n\n{body}"

# --- The Connection Logic ---
print("🚀 Starting the test...")
try:
    # Create a secure SSL context
    context = ssl.create_default_context()

    print("Attempting to connect to the server...")
    # Try to connect to the server
    server = smtplib.SMTP(smtp_server, port)
    
    print("Starting TLS encryption...")
    server.starttls(context=context) # Secure the connection
    
    print("Logging in...")
    server.login(sender_email, password)
    
    print("Sending the email...")
    server.sendmail(sender_email, receiver_email, message)
    
    print("\n✅ SUCCESS: The email was sent! Your credentials and connection are working.")

except Exception as e:
    print(f"\n❌ FAILED: The script ran into an error.")
    print(f"   Error Type: {type(e).__name__}")
    print(f"   Error Details: {e}")

finally:
    if 'server' in locals() and server:
        print("Closing the connection.")
        server.quit()