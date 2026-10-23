#[cfg(target_os = "windows")]
mod win32 {
    use std::ptr;

    #[repr(C)]
    #[derive(Clone, Copy, Debug)]
    pub struct MIB_TCPROW {
        pub state: u32,
        pub local_addr: u32,
        pub local_port: u32,
        pub remote_addr: u32,
        pub remote_port: u32,
    }

    #[repr(C)]
    pub struct MIB_TCPTABLE {
        pub num_entries: u32,
        pub table: [MIB_TCPROW; 1],
    }

    #[link(name = "advapi32")]
    unsafe extern "system" {
        fn ImpersonateAnonymousToken(ThreadHandle: *mut std::ffi::c_void) -> i32;
        fn RevertToSelf() -> i32;
    }

    #[link(name = "kernel32")]
    unsafe extern "system" {
        fn GetCurrentThread() -> *mut std::ffi::c_void;
        fn GetCurrentProcess() -> *mut std::ffi::c_void;
        fn CreateJobObjectW(
            lpJobAttributes: *mut std::ffi::c_void,
            lpName: *const u16,
        ) -> *mut std::ffi::c_void;
        fn AssignProcessToJobObject(
            hJob: *mut std::ffi::c_void,
            hProcess: *mut std::ffi::c_void,
        ) -> i32;
        fn SetInformationJobObject(
            hJob: *mut std::ffi::c_void,
            JobObjectInformationClass: u32,
            lpJobObjectInformation: *const std::ffi::c_void,
            cbJobObjectInformationLength: u32,
        ) -> i32;
        fn CloseHandle(hObject: *mut std::ffi::c_void) -> i32;
    }

    #[link(name = "iphlpapi")]
    unsafe extern "system" {
        fn GetTcpTable(pTcpTable: *mut MIB_TCPTABLE, pdwSize: *mut u32, bOrder: i32) -> u32;
        fn SetTcpEntry(pTcprow: *const MIB_TCPROW) -> u32;
    }

    #[repr(C)]
    #[allow(non_snake_case)]
    struct JOBOBJECT_BASIC_LIMIT_INFORMATION {
        PerProcessUserTimeLimit: i64,
        PerJobUserTimeLimit: i64,
        LimitFlags: u32,
        MinimumWorkingSetSize: usize,
        MaximumWorkingSetSize: usize,
        ActiveProcessLimit: u32,
        Affinity: usize,
        PriorityClass: u32,
        SchedulingClass: u32,
    }

    #[repr(C)]
    #[allow(non_snake_case)]
    struct IO_COUNTERS {
        ReadOperationCount: u64,
        WriteOperationCount: u64,
        OtherOperationCount: u64,
        ReadTransferCount: u64,
        WriteTransferCount: u64,
        OtherTransferCount: u64,
    }

    #[repr(C)]
    #[allow(non_snake_case)]
    struct JOBOBJECT_EXTENDED_LIMIT_INFORMATION {
        BasicLimitInformation: JOBOBJECT_BASIC_LIMIT_INFORMATION,
        IoInfo: IO_COUNTERS,
        ProcessMemoryLimit: usize,
        JobMemoryLimit: usize,
        PeakProcessMemoryLimit: usize,
        PeakJobMemoryLimit: usize,
    }

    const JOB_OBJECT_EXTENDED_LIMIT_INFORMATION: u32 = 9;
    const JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE: u32 = 0x00002000;

    pub fn create_kill_on_close_job() -> Result<*mut std::ffi::c_void, String> {
        unsafe {
            let job = CreateJobObjectW(ptr::null_mut(), ptr::null());
            if job.is_null() {
                let err = std::io::Error::last_os_error();
                return Err(format!("CreateJobObjectW failed: {}", err));
            }
            let mut info: JOBOBJECT_EXTENDED_LIMIT_INFORMATION = std::mem::zeroed();
            info.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE;
            let set_res = SetInformationJobObject(
                job,
                JOB_OBJECT_EXTENDED_LIMIT_INFORMATION,
                &info as *const _ as *const std::ffi::c_void,
                std::mem::size_of::<JOBOBJECT_EXTENDED_LIMIT_INFORMATION>() as u32,
            );
            if set_res == 0 {
                let err = std::io::Error::last_os_error();
                CloseHandle(job);
                return Err(format!("SetInformationJobObject failed: {}", err));
            }
            Ok(job)
        }
    }

    pub fn assign_process_to_job(
        job: *mut std::ffi::c_void,
        process: *mut std::ffi::c_void,
    ) -> Result<(), String> {
        unsafe {
            let res = AssignProcessToJobObject(job, process);
            if res != 0 {
                Ok(())
            } else {
                let err = std::io::Error::last_os_error();
                Err(format!("AssignProcessToJobObject failed: {}", err))
            }
        }
    }

    pub fn create_sandboxed_job() -> Result<usize, String> {
        unsafe {
            let job = CreateJobObjectW(ptr::null_mut(), ptr::null());
            if job.is_null() {
                let err = std::io::Error::last_os_error();
                return Err(format!("CreateJobObjectW failed: {}", err));
            }
            let cur_proc = GetCurrentProcess();
            let _ = AssignProcessToJobObject(job, cur_proc);
            // CloseHandle to let OS manage lifetime upon process exit
            CloseHandle(job);
            Ok(1)
        }
    }

    pub fn drop_thread_privileges() -> Result<(), String> {
        unsafe {
            let thread_handle = GetCurrentThread();
            let result = ImpersonateAnonymousToken(thread_handle);
            if result != 0 {
                Ok(())
            } else {
                let err = std::io::Error::last_os_error();
                Err(format!(
                    "Error calling ImpersonateAnonymousToken: {} (code {})",
                    err,
                    err.raw_os_error().unwrap_or(0)
                ))
            }
        }
    }

    pub fn restore_thread_privileges() -> Result<(), String> {
        unsafe {
            let result = RevertToSelf();
            if result != 0 {
                Ok(())
            } else {
                let err = std::io::Error::last_os_error();
                Err(format!(
                    "Error calling RevertToSelf: {} (code {})",
                    err,
                    err.raw_os_error().unwrap_or(0)
                ))
            }
        }
    }

    pub fn terminate_external_tcp_connections() -> Result<usize, String> {
        unsafe {
            let mut size: u32 = 0;
            // 1. Get size needed
            let _ = GetTcpTable(ptr::null_mut(), &mut size, 0);
            if size == 0 {
                return Ok(0);
            }

            // 2. Allocate buffer
            let mut buffer = vec![0u8; size as usize];
            let p_table = buffer.as_mut_ptr() as *mut MIB_TCPTABLE;

            // 3. Retrieve actual table
            let ret = GetTcpTable(p_table, &mut size, 0);
            if ret != 0 {
                return Err(format!("GetTcpTable failed with code {}", ret));
            }

            let table_ref = &*p_table;
            let num_entries = table_ref.num_entries as usize;

            // Pointer to table entries array
            let table_ptr = &table_ref.table as *const MIB_TCPROW;
            let mut closed_count = 0;

            for i in 0..num_entries {
                let row = *table_ptr.add(i);

                // remote_addr = 0 means listening or not connected
                if row.remote_addr == 0 {
                    continue;
                }

                // Check if it is a loopback address (127.x.x.x)
                let first_byte = row.remote_addr & 0xFF;
                if first_byte == 127 {
                    // Loopback connection - skip
                    continue;
                }

                // state = 5 is MIB_TCP_STATE_ESTAB (Established)
                // We want to terminate active connections by setting to state 12 (MIB_TCP_STATE_DELETE_TCB)
                let mut delete_row = row;
                delete_row.state = 12; // MIB_TCP_STATE_DELETE_TCB

                let set_ret = SetTcpEntry(&delete_row);
                if set_ret == 0 {
                    closed_count += 1;
                }
            }

            Ok(closed_count)
        }
    }
    #[repr(C)]
    #[allow(non_snake_case)]
    pub struct DATA_BLOB {
        pub cbData: u32,
        pub pbData: *mut u8,
    }

    #[link(name = "crypt32")]
    unsafe extern "system" {
        fn CryptProtectData(
            pDataIn: *const DATA_BLOB,
            szDataDescr: *const u16,
            pOptionalEntropy: *const DATA_BLOB,
            pvReserved: *mut std::ffi::c_void,
            pPromptStruct: *mut std::ffi::c_void,
            dwFlags: u32,
            pDataOut: *mut DATA_BLOB,
        ) -> i32;

        fn CryptUnprotectData(
            pDataIn: *const DATA_BLOB,
            ppszDataDescr: *mut *mut u16,
            pOptionalEntropy: *const DATA_BLOB,
            pvReserved: *mut std::ffi::c_void,
            pPromptStruct: *mut std::ffi::c_void,
            dwFlags: u32,
            pDataOut: *mut DATA_BLOB,
        ) -> i32;
    }

    #[link(name = "kernel32")]
    unsafe extern "system" {
        fn LocalFree(hMem: *mut std::ffi::c_void) -> *mut std::ffi::c_void;
    }

    pub fn protect_secret(plaintext: &[u8]) -> Result<Vec<u8>, String> {
        let mut dummy = 0u8;
        let pb_data = if plaintext.is_empty() {
            &mut dummy as *mut u8
        } else {
            plaintext.as_ptr() as *mut u8
        };
        unsafe {
            let in_blob = DATA_BLOB {
                cbData: plaintext.len() as u32,
                pbData: pb_data,
            };
            let mut out_blob = DATA_BLOB {
                cbData: 0,
                pbData: ptr::null_mut(),
            };

            let res = CryptProtectData(
                &in_blob,
                ptr::null(),
                ptr::null(),
                ptr::null_mut(),
                ptr::null_mut(),
                0,
                &mut out_blob,
            );

            if res != 0 && !out_blob.pbData.is_null() {
                let slice = std::slice::from_raw_parts(out_blob.pbData, out_blob.cbData as usize);
                let result = slice.to_vec();
                LocalFree(out_blob.pbData as *mut std::ffi::c_void);
                Ok(result)
            } else {
                let err = std::io::Error::last_os_error();
                Err(format!(
                    "DPAPI CryptProtectData failed: {} (code {})",
                    err,
                    err.raw_os_error().unwrap_or(0)
                ))
            }
        }
    }

    pub fn unprotect_secret(ciphertext: &[u8]) -> Result<Vec<u8>, String> {
        if ciphertext.is_empty() {
            return Err("Nieprawidłowy format zaszyfrowanego sekretu (pusty bufor).".to_string());
        }
        unsafe {
            let in_blob = DATA_BLOB {
                cbData: ciphertext.len() as u32,
                pbData: ciphertext.as_ptr() as *mut u8,
            };
            let mut out_blob = DATA_BLOB {
                cbData: 0,
                pbData: ptr::null_mut(),
            };

            let res = CryptUnprotectData(
                &in_blob,
                ptr::null_mut(),
                ptr::null(),
                ptr::null_mut(),
                ptr::null_mut(),
                0,
                &mut out_blob,
            );

            if res != 0 && !out_blob.pbData.is_null() {
                let slice = std::slice::from_raw_parts(out_blob.pbData, out_blob.cbData as usize);
                let result = slice.to_vec();
                LocalFree(out_blob.pbData as *mut std::ffi::c_void);
                Ok(result)
            } else {
                let err = std::io::Error::last_os_error();
                Err(format!(
                    "DPAPI CryptUnprotectData failed: {} (code {})",
                    err,
                    err.raw_os_error().unwrap_or(0)
                ))
            }
        }
    }
}

#[cfg(target_os = "windows")]
pub use win32::{
    assign_process_to_job, create_kill_on_close_job, create_sandboxed_job, drop_thread_privileges,
    protect_secret, restore_thread_privileges, terminate_external_tcp_connections,
    unprotect_secret,
};

#[cfg(not(target_os = "windows"))]
pub fn create_kill_on_close_job() -> Result<*mut std::ffi::c_void, String> {
    Ok(std::ptr::null_mut())
}

#[cfg(not(target_os = "windows"))]
pub fn assign_process_to_job(
    _job: *mut std::ffi::c_void,
    _process: *mut std::ffi::c_void,
) -> Result<(), String> {
    Ok(())
}

#[cfg(not(target_os = "windows"))]
pub fn create_sandboxed_job() -> Result<usize, String> {
    println!("🛡️ [STUB]: Job Object Sandbox (dostępny na Windows).");
    Ok(0)
}

#[cfg(not(target_os = "windows"))]
pub fn drop_thread_privileges() -> Result<(), String> {
    println!("🛡️ [STUB]: Zrzucenie uprawnień wątku (dostępne tylko na Windows).");
    Ok(())
}

#[cfg(not(target_os = "windows"))]
pub fn restore_thread_privileges() -> Result<(), String> {
    println!("🛡️ [STUB]: Przywrócenie uprawnień wątku (dostępne tylko na Windows).");
    Ok(())
}

#[cfg(not(target_os = "windows"))]
pub fn terminate_external_tcp_connections() -> Result<usize, String> {
    println!("🛡️ [STUB]: Zrywanie połączeń sieciowych (dostępne tylko na Windows).");
    Ok(0)
}

#[cfg(any(not(target_os = "windows"), test))]
pub(crate) mod unix_vault {
    use sha2::{Digest, Sha256};
    use std::fs;
    use std::path::PathBuf;

    const MAGIC: &[u8; 4] = b"BLY1";

    fn hmac_sha256(key: &[u8], data: &[u8]) -> [u8; 32] {
        let mut k_pad = [0u8; 64];
        if key.len() > 64 {
            let mut hasher = Sha256::new();
            hasher.update(key);
            let h = hasher.finalize();
            k_pad[..32].copy_from_slice(&h);
        } else {
            k_pad[..key.len()].copy_from_slice(key);
        }

        let mut ipad = [0x36u8; 64];
        let mut opad = [0x5cu8; 64];
        for i in 0..64 {
            ipad[i] ^= k_pad[i];
            opad[i] ^= k_pad[i];
        }

        let mut inner = Sha256::new();
        inner.update(ipad);
        inner.update(data);
        let inner_hash = inner.finalize();

        let mut outer = Sha256::new();
        outer.update(opad);
        outer.update(inner_hash);
        outer.finalize().into()
    }

    fn get_or_create_vault_master_key() -> Result<[u8; 32], String> {
        let home = std::env::var_os("HOME").ok_or_else(|| {
            "Brak zmiennej środowiskowej HOME: brak zaufanego katalogu użytkownika dla sejfu."
                .to_string()
        })?;
        let config_dir = PathBuf::from(home).join(".config").join("blyskawica");
        fs::create_dir_all(&config_dir)
            .map_err(|e| format!("Błąd tworzenia katalogu konfiguracyjnego sejfu: {}", e))?;

        #[cfg(unix)]
        {
            use std::os::unix::fs::PermissionsExt;
            let _ = fs::set_permissions(&config_dir, fs::Permissions::from_mode(0o700));
        }

        let key_file = config_dir.join(".vault_master.key");

        if key_file.exists() {
            let bytes =
                fs::read(&key_file).map_err(|e| format!("Błąd odczytu klucza sejfu: {}", e))?;
            if bytes.len() == 32 {
                let mut key = [0u8; 32];
                key.copy_from_slice(&bytes);
                return Ok(key);
            }
            return Err("Klucz sejfu ma nieprawidłową długość.".to_string());
        }

        let mut raw_key = [0u8; 32];
        rand::Rng::fill(&mut rand::thread_rng(), &mut raw_key);

        let pid = std::process::id();
        let mut unique_bytes = [0u8; 8];
        rand::Rng::fill(&mut rand::thread_rng(), &mut unique_bytes);
        let unique = u64::from_le_bytes(unique_bytes);
        let tmp_key_file = config_dir.join(format!(".vault_master.tmp.{pid}.{unique}"));

        #[cfg(unix)]
        {
            use std::io::Write;
            use std::os::unix::fs::OpenOptionsExt;
            let mut file = fs::OpenOptions::new()
                .write(true)
                .create_new(true)
                .mode(0o600)
                .open(&tmp_key_file)
                .map_err(|e| {
                    format!(
                        "Błąd bezpiecznego tworzenia pliku tymczasowego klucza: {}",
                        e
                    )
                })?;
            file.write_all(&raw_key)
                .map_err(|e| format!("Błąd zapisu klucza do pliku tymczasowego: {}", e))?;
            file.flush()
                .map_err(|e| format!("Błąd zapisu buforowanego klucza: {}", e))?;
        }
        #[cfg(not(unix))]
        {
            fs::write(&tmp_key_file, raw_key)
                .map_err(|e| format!("Błąd zapisu klucza sejfu: {}", e))?;
        }

        if let Err(rename_err) = fs::rename(&tmp_key_file, &key_file) {
            let _ = fs::remove_file(&tmp_key_file);
            if key_file.exists() {
                if let Ok(bytes) = fs::read(&key_file) {
                    if bytes.len() == 32 {
                        let mut key = [0u8; 32];
                        key.copy_from_slice(&bytes);
                        return Ok(key);
                    }
                }
            }
            return Err(format!(
                "Nie udało się zainicjalizować klucza sejfu: {}",
                rename_err
            ));
        }

        Ok(raw_key)
    }

    fn derive_subkeys() -> Result<([u8; 32], [u8; 32]), String> {
        let master = get_or_create_vault_master_key()?;
        let mut machine_binding = Vec::new();
        if let Ok(id) = fs::read_to_string("/etc/machine-id") {
            machine_binding.extend_from_slice(id.trim().as_bytes());
        } else if let Ok(id) = fs::read_to_string("/var/lib/dbus/machine-id") {
            machine_binding.extend_from_slice(id.trim().as_bytes());
        }
        if let Ok(user) = std::env::var("USER") {
            machine_binding.extend_from_slice(user.as_bytes());
        }

        let mut enc_ctx = b"BLY_VAULT_ENC_V1_".to_vec();
        enc_ctx.extend_from_slice(&machine_binding);
        let k_enc = hmac_sha256(&master, &enc_ctx);

        let mut mac_ctx = b"BLY_VAULT_MAC_V1_".to_vec();
        mac_ctx.extend_from_slice(&machine_binding);
        let k_mac = hmac_sha256(&master, &mac_ctx);

        Ok((k_enc, k_mac))
    }

    fn keystream_xor(k_enc: &[u8; 32], nonce: &[u8; 16], data: &mut [u8]) {
        for (i, chunk) in data.chunks_mut(32).enumerate() {
            let mut counter_buf = [0u8; 24];
            counter_buf[..16].copy_from_slice(nonce);
            counter_buf[16..24].copy_from_slice(&(i as u64).to_le_bytes());
            let stream_block = hmac_sha256(k_enc, &counter_buf);
            for (byte, s) in chunk.iter_mut().zip(stream_block.iter()) {
                *byte ^= *s;
            }
        }
    }

    pub fn protect_secret(plaintext: &[u8]) -> Result<Vec<u8>, String> {
        let (k_enc, k_mac) = derive_subkeys()?;

        let mut nonce = [0u8; 16];
        rand::Rng::fill(&mut rand::thread_rng(), &mut nonce);

        let mut ciphertext = plaintext.to_vec();
        keystream_xor(&k_enc, &nonce, &mut ciphertext);

        let mut mac_input = Vec::with_capacity(4 + 16 + ciphertext.len());
        mac_input.extend_from_slice(MAGIC);
        mac_input.extend_from_slice(&nonce);
        mac_input.extend_from_slice(&ciphertext);
        let tag = hmac_sha256(&k_mac, &mac_input);

        let mut result = Vec::with_capacity(4 + 16 + 32 + ciphertext.len());
        result.extend_from_slice(MAGIC);
        result.extend_from_slice(&nonce);
        result.extend_from_slice(&tag);
        result.extend_from_slice(&ciphertext);
        Ok(result)
    }

    pub fn unprotect_secret(ciphertext: &[u8]) -> Result<Vec<u8>, String> {
        if ciphertext.len() < 4 + 16 + 32 {
            return Err("Nieprawidłowy format zaszyfrowanego sekretu (zbyt krótki).".to_string());
        }
        if &ciphertext[..4] != MAGIC {
            return Err("Nieprawidłowy nagłówek sejfu (nieznany format BLY).".to_string());
        }

        let (k_enc, k_mac) = derive_subkeys()?;

        let mut nonce = [0u8; 16];
        nonce.copy_from_slice(&ciphertext[4..20]);

        let expected_tag = &ciphertext[20..52];
        let encrypted_body = &ciphertext[52..];

        let mut mac_input = Vec::with_capacity(4 + 16 + encrypted_body.len());
        mac_input.extend_from_slice(MAGIC);
        mac_input.extend_from_slice(&nonce);
        mac_input.extend_from_slice(encrypted_body);
        let computed_tag = hmac_sha256(&k_mac, &mac_input);

        let mut diff = 0u8;
        for (a, b) in expected_tag.iter().zip(computed_tag.iter()) {
            diff |= *a ^ *b;
        }
        if diff != 0 {
            return Err(
                "Błąd weryfikacji HMAC: naruszona integralność sejfu lub nieprawidłowy klucz."
                    .to_string(),
            );
        }

        let mut plaintext = encrypted_body.to_vec();
        keystream_xor(&k_enc, &nonce, &mut plaintext);
        Ok(plaintext)
    }
}

#[cfg(not(target_os = "windows"))]
pub use unix_vault::{protect_secret, unprotect_secret};

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_privilege_flow() {
        // Test drop privilege flow
        let res = drop_thread_privileges();
        assert!(
            res.is_ok(),
            "Zrzucenie uprawnień powinno się udać lub wywołać stub"
        );

        // Próba zapisu pliku powinna się nie udać na Windows w trybie Anonymous
        #[cfg(target_os = "windows")]
        {
            let test_path = std::env::current_dir().unwrap().join("test_anon_write.txt");
            let write_res = std::fs::write(&test_path, "test");
            assert!(
                write_res.is_err(),
                "Zapis pliku w trybie Anonymous powinien zakończyć się błędem."
            );
        }

        let restore_res = restore_thread_privileges();
        assert!(
            restore_res.is_ok(),
            "Przywrócenie uprawnień powinno się udać lub wywołać stub"
        );

        // Po przywróceniu, zapis powinien zadziałać
        #[cfg(target_os = "windows")]
        {
            let test_path = std::env::current_dir().unwrap().join("test_anon_write.txt");
            let write_res = std::fs::write(&test_path, "test");
            assert!(
                write_res.is_ok(),
                "Zapis pliku po przywróceniu uprawnień powinien zadziałać."
            );
            let _ = std::fs::remove_file(test_path);
        }
    }

    #[test]
    fn test_tcp_list() {
        let res = terminate_external_tcp_connections();
        assert!(res.is_ok());
    }

    #[test]
    fn test_vault_protect_unprotect() {
        let secret = b"blyskawica_vault_test_secret_12345";
        let encrypted = protect_secret(secret).expect("Vault protect should succeed");
        assert_ne!(encrypted, secret, "Ciphertext should differ from plaintext");

        let decrypted = unprotect_secret(&encrypted).expect("Vault unprotect should succeed");
        assert_eq!(
            decrypted, secret,
            "Decrypted secret must match original plaintext"
        );

        let mut tampered = encrypted.clone();
        let last = tampered.len() - 1;
        tampered[last] ^= 0x01;
        assert!(
            unprotect_secret(&tampered).is_err(),
            "Tampered vault payload must fail decryption/validation"
        );

        // Test empty plaintext roundtrip
        let empty_enc = protect_secret(b"").expect("Empty payload protection should succeed");
        let empty_dec =
            unprotect_secret(&empty_enc).expect("Empty payload unprotection should succeed");
        assert!(
            empty_dec.is_empty(),
            "Decrypted empty payload must be empty"
        );

        // Test raw empty ciphertext rejection
        assert!(
            unprotect_secret(&[]).is_err(),
            "Raw empty ciphertext must fail validation"
        );
    }

    #[test]
    fn test_unix_vault_envelope_and_validation() {
        let mut unique_bytes = [0u8; 8];
        rand::Rng::fill(&mut rand::thread_rng(), &mut unique_bytes);
        let unique = u64::from_le_bytes(unique_bytes);
        let temp_dir = std::env::temp_dir().join(format!("blyskawica_unix_vault_test_{unique}"));
        let _ = std::fs::create_dir_all(&temp_dir);
        let orig_home = std::env::var_os("HOME");
        unsafe {
            std::env::set_var("HOME", &temp_dir);
        }

        // 1. Normal secret roundtrip
        let secret = b"super_secret_cross_platform_payload_123";
        let encrypted = unix_vault::protect_secret(secret).expect("protect should succeed");
        assert!(encrypted.len() >= 52);
        assert_eq!(&encrypted[..4], b"BLY1");
        let decrypted = unix_vault::unprotect_secret(&encrypted).expect("unprotect should succeed");
        assert_eq!(decrypted, secret);

        // 2. Empty plaintext produces valid 52-byte envelope
        let empty_enc = unix_vault::protect_secret(b"").expect("protect empty should succeed");
        assert_eq!(empty_enc.len(), 52);
        let empty_dec =
            unix_vault::unprotect_secret(&empty_enc).expect("unprotect empty should succeed");
        assert!(empty_dec.is_empty());

        // 3. Short / truncated ciphertext rejection
        assert!(unix_vault::unprotect_secret(&[]).is_err());
        assert!(unix_vault::unprotect_secret(b"BLY1").is_err());
        assert!(unix_vault::unprotect_secret(&encrypted[..51]).is_err());

        // 4. Tampering rejection
        let mut tampered = encrypted.clone();
        let len = tampered.len();
        tampered[len - 1] ^= 0x42;
        assert!(unix_vault::unprotect_secret(&tampered).is_err());

        // Clean up
        let _ = std::fs::remove_dir_all(&temp_dir);
        unsafe {
            if let Some(h) = orig_home {
                std::env::set_var("HOME", h);
            } else {
                std::env::remove_var("HOME");
            }
        }
    }

    #[test]
    fn test_sandboxed_job_object() {
        let res = create_sandboxed_job();
        assert!(
            res.is_ok(),
            "Utworzenie i przypisanie Job Object sandboxu powinno się powieść"
        );
    }
}
