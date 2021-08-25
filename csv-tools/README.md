# CSV Tools

## Split CSV

Takes a CSV file and generates multiple CSV files containing the same rows
in total, each generated file is limited to a maximum number of rows.

Features:

- The order of rows is preserved: each generated file is named after the 
    original file but marked with a number and the row range contained. 
- The resulting files are not overwritten to avoid accidental data loss.
- The original file is read in parts so any length should be supported.

Syntax:

```shell
python split_csv.py CSV_FILE MAX_ROWS HAS_HEADERS
```

- `CSV_FILE`: Required. Original CSV file. Path can be relative or absolute.
- `MAX_ROWS`: Required. Maximum number of rows in the resulting files 
    (excluding header row).
- `HAS_HEADERS`: Optional. Defaults to `1`, meaning that the first row
    represents the headers. When equal to `0`, the first row is treated as
    a normal row and resulting files won't contain headers.
