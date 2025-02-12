import pandas
import torch
import CONSTANS


def checkPosition(df: pandas.DataFrame, isVertical: bool, isBlack: bool) -> dict:
    xBoard_start = df.loc[df.name == 'Board'].xmin
    xBoard_end = df.loc[df.name == 'Board'].xmax
    yBoard_start = df.loc[df.name == 'Board'].ymin
    yBoard_end = df.loc[df.name == 'Board'].ymax
    x_row_size = (xBoard_end - xBoard_start) / 8
    y_row_size = (yBoard_end - yBoard_start) / 8
    df = df[df.name != 'Board']
    figures = {
        'black': {
            'draught': {},
            'king': {}
        },
        'white': {
            'draught': {},
            'king': {}
        }
    }
    for i, row in df.iterrows():
        figure_type = row['name'].split('_')
        x_center = (row.xmin + row.xmax) / 2
        y_center = (row.ymin + row.ymax) / 2
        x_coord = -1
        y_coord = -1
        for j in range(8):
            if float(xBoard_start + j * x_row_size) <= x_center <= float(xBoard_start + (j + 1) * x_row_size):
                x_coord = j
                break
        for j in range(8):
            if float(yBoard_start + j * y_row_size) <= y_center <= float(yBoard_start + (j + 1) * y_row_size):
                y_coord = j
                break
        if x_coord != -1 and y_coord != -1:
            if isVertical:
                if isBlack:
                    cell = f"{CONSTANS.rowLetters[7 - x_coord]}{y_coord + 1}"
                    if cell not in figures[figure_type[0].lower()][figure_type[1].lower()].keys():
                        figures[figure_type[0].lower()][figure_type[1].lower()][cell] = row.confidence
                    else:
                        if row.confidence > figures[figure_type[0].lower()][figure_type[1].lower()][cell]:
                            figures[figure_type[0].lower()][figure_type[1].lower()][cell] = row.confidence
                else:
                    cell = f"{CONSTANS.rowLetters[x_coord]}{8 - y_coord}"
                    if cell not in figures[figure_type[0].lower()][figure_type[1].lower()].keys():
                        figures[figure_type[0].lower()][figure_type[1].lower()][cell] = row.confidence
                    else:
                        if row.confidence > figures[figure_type[0].lower()][figure_type[1].lower()][cell]:
                            figures[figure_type[0].lower()][figure_type[1].lower()][cell] = row.confidence
            else:
                if isBlack:
                    cell = f"{CONSTANS.rowLetters[7 - y_coord]}{8 - x_coord}"
                    if cell not in figures[figure_type[0].lower()][figure_type[1].lower()].keys():
                        figures[figure_type[0].lower()][figure_type[1].lower()][cell] = row.confidence
                    else:
                        if row.confidence > figures[figure_type[0].lower()][figure_type[1].lower()][cell]:
                            figures[figure_type[0].lower()][figure_type[1].lower()][cell] = row.confidence
                else:
                    cell = f"{CONSTANS.rowLetters[y_coord]}{x_coord + 1}"
                    if cell not in figures[figure_type[0].lower()][figure_type[1].lower()].keys():
                        figures[figure_type[0].lower()][figure_type[1].lower()][cell] = row.confidence
                    else:
                        if row.confidence > figures[figure_type[0].lower()][figure_type[1].lower()][cell]:
                            figures[figure_type[0].lower()][figure_type[1].lower()][cell] = row.confidence
    return figures

# FEN Формат: "(W/B):W(Ka3/a3):B(Ka3/a3)"
def figuresToFEN(figures: dict) -> str:
    white_figures = []
    black_figures = []
    for white_draught in figures['white']['draught'].keys():
        white_figures.append(white_draught)
    for black_draught in figures['black']['draught'].keys():
        black_figures.append(black_draught)
    for white_king in figures['white']['king'].keys():
        white_figures.append(f"K{white_king}")
    for black_king in figures['black']['king'].keys():
        black_figures.append(f"K{black_king}")
    return f"\nХод белых: W:W{','.join(white_figures)}:B{','.join(black_figures)}\n" \
           f"Ход чёрных: B:W{','.join(white_figures)}:B{','.join(black_figures)}"


def posToFEN(dfList: list, isVertical: bool, isBlack: bool) -> str:
    i = 1
    s = ""
    for elem in dfList:
        if not (elem.name == 'Board').any():
            s += f"Позиция №{i}: Не удалось распознать позицию\n"
        else:
            s += f"Позиция №{i}: {figuresToFEN(checkPosition(elem, isVertical, isBlack))}\n\n"
        i += 1
    return s


def start(paths: list, isVertical: bool, isBlack: bool) -> str:
    model = torch.hub.load('./yolov5', 'custom', path='model/best1.pt', source='local')
    model.conf = 0.6
    results = model(paths)
    return posToFEN(results.pandas().xyxy, isVertical, isBlack)


print(start(CONSTANS.detect_vertical_white, True, False))
print(start(CONSTANS.detect_vertical_black, True, True))
print(start(CONSTANS.detect_horizontal_white, False, False))
print(start(CONSTANS.detect_horizontal_black, False, True))
