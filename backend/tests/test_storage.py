import os
import pytest
from app.services.storage_service import storage_service

def test_encrypted_storage_upload_and_retrieve():
    original_text = "CONFIDENTIAL MAHARASHTRA LEAVE AND LICENSE AGREEMENT BETWEEN LANDLORD AND TENANT"
    original_bytes = original_text.encode('utf-8')
    
    meta = storage_service.upload_file("test_contract.txt", original_bytes)
    assert meta["encrypted"] is True
    assert "file_key" in meta
    assert meta["size_bytes"] == len(original_bytes)
    
    file_key = meta["file_key"]
    
    # Decrypt via storage service and verify matching original content
    decrypted_bytes = storage_service.fetch_file(file_key)
    assert decrypted_bytes == original_bytes
    assert decrypted_bytes.decode('utf-8') == original_text

    # Clean up local file if created
    if os.path.exists(file_key):
        with open(file_key, "rb") as f:
            stored_bytes = f.read()
        assert original_bytes not in stored_bytes # Payload on disk must be encrypted ciphertext
        os.remove(file_key)
