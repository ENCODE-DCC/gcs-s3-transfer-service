from gcs_s3_transfer_service import app

if __name__ == "__main__":
    # This is used when running locally only. On Google App Engine, a production-grade
    # WSGI server will be used automatically.
    app.run(host="127.0.0.1", port=8080, debug=True)
