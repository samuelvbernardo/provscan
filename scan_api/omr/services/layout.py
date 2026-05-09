from math import ceil


PAGE_WIDTH_MM = 210
PAGE_HEIGHT_MM = 297

READ_AREA_LEFT_MM = 12
READ_AREA_RIGHT_MM = 198
READ_AREA_TOP_MM = 12
READ_AREA_BOTTOM_MM = 190
MARKER_SIZE_MM = 7

STUDENT_NUMBER_START_X_MM = 25
STUDENT_NUMBER_START_Y_MM = 78
STUDENT_NUMBER_ROW_GAP_MM = 7
STUDENT_NUMBER_COLUMNS_X_MM = [43, 57]

QUESTIONS_COLUMNS = 2
QUESTIONS_START_X_MM = 68
QUESTIONS_START_Y_MM = 78
QUESTION_ROW_GAP_MM = 7
QUESTION_OPTION_GAP_MM = 8
QUESTION_OPTION_START_OFFSET_MM = 15
QUESTION_LETTER_START_OFFSET_MM = 14
QUESTION_COLUMN_WIDTH_4_OPTIONS_MM = 50
QUESTION_COLUMN_WIDTH_5_OPTIONS_MM = 60


def questions_per_column(questions_count):
    return ceil(questions_count / QUESTIONS_COLUMNS)


def question_column_width_mm(options_count):
    if options_count == 5:
        return QUESTION_COLUMN_WIDTH_5_OPTIONS_MM

    return QUESTION_COLUMN_WIDTH_4_OPTIONS_MM


def question_position_mm(question_index, questions_count, options_count):
    per_column = questions_per_column(questions_count)
    column = question_index // per_column
    row = question_index % per_column

    x = QUESTIONS_START_X_MM + column * question_column_width_mm(options_count)
    y = QUESTIONS_START_Y_MM + row * QUESTION_ROW_GAP_MM

    return x, y


def question_option_x_mm(question_base_x_mm, option_index):
    return (
        question_base_x_mm
        + QUESTION_OPTION_START_OFFSET_MM
        + option_index * QUESTION_OPTION_GAP_MM
    )


def question_letter_x_mm(question_base_x_mm, option_index):
    return (
        question_base_x_mm
        + QUESTION_LETTER_START_OFFSET_MM
        + option_index * QUESTION_OPTION_GAP_MM
    )
