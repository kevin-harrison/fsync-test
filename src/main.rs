use rand::Rng;
use std::fs::File;
use std::io::{self, Write};
use std::time::{Duration, Instant};

fn duration_to_nanos(d: &Duration) -> u128 {
    d.as_secs() as u128 * 1_000_000_000 + d.subsec_nanos() as u128
}

fn average_duration(durations: Vec<Duration>) -> Option<(Duration, Duration)> {
    if durations.is_empty() {
        return None; // No durations to average
    }
    let total_nanos: u128 = durations.iter().map(duration_to_nanos).sum();
    let mean_nanos = total_nanos / durations.len() as u128;
    let variance_nanos: u128 = durations
        .iter()
        .map(|d| {
            let nanos = duration_to_nanos(d);
            let diff = nanos as i128 - mean_nanos as i128;
            (diff * diff) as u128
        })
        .sum::<u128>()
        / durations.len() as u128;
    let std_dev_nanos = (variance_nanos as f64).sqrt() as u128;
    let std_dev_duration = Duration::new(
        (std_dev_nanos / 1_000_000_000) as u64, // seconds
        (std_dev_nanos % 1_000_000_000) as u32, // nanoseconds
    );
    let mean_duration = Duration::new(
        (mean_nanos / 1_000_000_000) as u64, // seconds
        (mean_nanos % 1_000_000_000) as u32, // nanoseconds
    );
    Some((mean_duration, std_dev_duration))
}

fn normal_file_write_test(data_size: usize) -> io::Result<()> {
    let mut file = File::create("output.bin")?;
    let mut latencies = vec![];

    let mut rng = rand::thread_rng();
    for i in 0..100 {
        let rand_int = rng.gen_range(0..i + 1);
        let buffer = vec![b'A' & rand_int; data_size];
        let start = Instant::now();
        file.write_all(&buffer)?;
        file.sync_all()?;
        latencies.push(Instant::now() - start);
    }
    let (average, std_dev) = average_duration(latencies).unwrap();
    eprintln!("{data_size:<8}, {average:<18?}, {std_dev:?}");
    println!("{data_size}, {average:?}, {std_dev:?}");
    Ok(())
}

fn main() {
    eprintln!("datasize, write_duration_avg, write_duration_std_dev");
    println!("datasize, write_duration_avg, write_duration_std_dev");
    for data_size in [8, 128, 256, 512, 1024, 2048, 4096, 8194, 16384, 32768] {
        // for data_size in [8] {
        normal_file_write_test(data_size).unwrap();
    }
}
