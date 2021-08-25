import os
import sys
import csv


def main():
    if len(sys.argv) < 3:
        raise Exception(
            f'Syntax: {sys.argv[0]} CSV_FILE MAX_ROWS [HAS_HEADERS]')

    csv_file = str(sys.argv[1])
    max_rows = int(sys.argv[2])
    has_headers = int(sys.argv[3]) if len(sys.argv) >= 4 else 1

    split(csv_file, max_rows, has_headers)


def split(csv_file, max_rows, has_headers):
    print('-' * 50)
    print(f'    CSV File : {csv_file}')
    print(f'    Max Rows : {max_rows}')
    print(f' Has Headers : {has_headers}')
    print('-' * 50)

    if max_rows <= 0:
        raise Exception(f'Invalid value for Max Rows: {max_rows}')

    chunks_enumerated = enumerate(iterate_chunks(
        csv_file, max_rows, has_headers))

    current_count = 0

    for chunk_index, (header_row, content_rows) in chunks_enumerated:
        end_count = current_count + len(content_rows)

        # Generate new file name
        info = f'{chunk_index+1:03d}-{current_count}-{end_count}'
        name, ext = os.path.splitext(csv_file)
        new_file = f'{name}({info}){ext}'

        create_csv(new_file, header_row, content_rows)

        current_count = end_count

    print(f'Done! total rows: {current_count}')


def iterate_chunks(csv_file, max_rows, has_headers):
    print(f'Reading {csv_file}...')

    header_row = None

    with open(csv_file, newline='') as csv_stream:
        csv_reader = csv.reader(csv_stream)
        row_buffer = []

        for row_index, row in enumerate(csv_reader):
            if row_index == 0 and has_headers:
                header_row = row
            else:
                row_buffer.append(row)

                if len(row_buffer) == max_rows:
                    yield header_row, row_buffer

                    row_buffer.clear()

        if len(row_buffer) > 0:
            yield header_row, row_buffer

            row_buffer.clear()


def create_csv(file_name, header_row, content_rows):
    print(f'Writing {file_name}...')

    with open(file_name, 'x', newline='') as csv_stream:
        csv_writer = csv.writer(csv_stream)

        if header_row is not None:
            csv_writer.writerow(header_row)

        csv_writer.writerows(content_rows)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e, file=sys.stderr)
