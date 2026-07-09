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
    }

    #[link(name = "iphlpapi")]
    unsafe extern "system" {
        fn GetTcpTable(
            pTcpTable: *mut MIB_TCPTABLE,
            pdwSize: *mut u32,
            bOrder: i32,
        ) -> u32;
        fn SetTcpEntry(pTcprow: *const MIB_TCPROW) -> u32;
    }

    pub fn drop_thread_privileges() -> Result<(), String> {
        unsafe {
            let thread_handle = GetCurrentThread();
            let result = ImpersonateAnonymousToken(thread_handle);
            if result != 0 {
                Ok(())
            } else {
                let err = std::io::Error::last_os_error();
                Err(format!("Error calling ImpersonateAnonymousToken: {} (code {})", err, err.raw_os_error().unwrap_or(0)))
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
                Err(format!("Error calling RevertToSelf: {} (code {})", err, err.raw_os_error().unwrap_or(0)))
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
}

#[cfg(target_os = "windows")]
pub use win32::{drop_thread_privileges, restore_thread_privileges, terminate_external_tcp_connections};

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

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_privilege_flow() {
        // Test drop privilege flow
        let res = drop_thread_privileges();
        assert!(res.is_ok(), "Zrzucenie uprawnień powinno się udać lub wywołać stub");

        // Próba zapisu pliku powinna się nie udać na Windows w trybie Anonymous
        #[cfg(target_os = "windows")]
        {
            let test_path = std::env::current_dir().unwrap().join("test_anon_write.txt");
            let write_res = std::fs::write(&test_path, "test");
            assert!(write_res.is_err(), "Zapis pliku w trybie Anonymous powinien zakończyć się błędem.");
        }

        let restore_res = restore_thread_privileges();
        assert!(restore_res.is_ok(), "Przywrócenie uprawnień powinno się udać lub wywołać stub");

        // Po przywróceniu, zapis powinien zadziałać
        #[cfg(target_os = "windows")]
        {
            let test_path = std::env::current_dir().unwrap().join("test_anon_write.txt");
            let write_res = std::fs::write(&test_path, "test");
            assert!(write_res.is_ok(), "Zapis pliku po przywróceniu uprawnień powinien zadziałać.");
            let _ = std::fs::remove_file(test_path);
        }
    }

    #[test]
    fn test_tcp_list() {
        let res = terminate_external_tcp_connections();
        assert!(res.is_ok());
    }
}
