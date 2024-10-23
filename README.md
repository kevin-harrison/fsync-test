To run:
`cargo run --release 1> output.csv`

To see calls to fsync:
`strace -c -e trace=fsync cargo run --release`
