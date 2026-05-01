import cv2
import numpy as np

from .preprocess import preprocess_image_from_array
from .detect import find_bubbles


IMAGE_WIDTH = 600
IMAGE_HEIGHT = 800

LETRAS = ["A", "B", "C", "D", "E"]


def score_bolha(image, thresh, x_centro, y_centro, raio=4):
    """
    Lê apenas o centro da bolha.
    Isso evita contar a borda da bolha vazia.
    """

    x1 = max(int(x_centro - raio), 0)
    x2 = min(int(x_centro + raio), IMAGE_WIDTH)

    y1 = max(int(y_centro - raio), 0)
    y2 = min(int(y_centro + raio), IMAGE_HEIGHT)

    roi_thresh = thresh[y1:y2, x1:x2]

    if roi_thresh.size == 0:
        score_thresh = 0
    else:
        total = cv2.countNonZero(roi_thresh)
        area = roi_thresh.shape[0] * roi_thresh.shape[1]
        score_thresh = total / float(area)

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    roi_hsv = hsv[y1:y2, x1:x2]

    if roi_hsv.size == 0:
        score_cor = 0
    else:
        saturacao = roi_hsv[:, :, 1]
        score_cor = cv2.mean(saturacao)[0] / 255.0

    return max(score_thresh, score_cor)


def clusterizar_valores(valores, tolerancia=12):
    """
    Agrupa valores próximos e retorna os centros dos grupos.
    Exemplo: vários X parecidos viram uma coluna.
    """

    if not valores:
        return []

    valores = sorted(valores)
    grupos = []

    for valor in valores:
        if not grupos:
            grupos.append([valor])
            continue

        media_grupo = sum(grupos[-1]) / len(grupos[-1])

        if abs(valor - media_grupo) <= tolerancia:
            grupos[-1].append(valor)
        else:
            grupos.append([valor])

    centros = [sum(grupo) / len(grupo) for grupo in grupos]

    return centros


def inferir_linhas_regulares(ys_detectados, quantidade, tolerancia_gap=4):
    """
    A partir das linhas detectadas, tenta inferir uma grade regular.

    Importante:
    Não tenta voltar uma linha para cima.
    Usa a primeira linha detectada como início real da tabela.
    """

    if not ys_detectados:
        return []

    ys = sorted(ys_detectados)

    if len(ys) >= 2:
        gaps = [ys[i + 1] - ys[i] for i in range(len(ys) - 1)]
        gaps_validos = [g for g in gaps if g > 10]

        if gaps_validos:
            gap = float(np.median(gaps_validos))
        else:
            gap = 22.0
    else:
        gap = 22.0

    # Antes o código voltava uma linha para cima.
    # Isso estava deslocando tudo.
    inicio = ys[0]

    linhas = [inicio + i * gap for i in range(quantidade)]

    return linhas


def escolher_marcacao(scores, limite_minimo=0.35, diferenca_minima=0.12):
    """
    Escolhe o índice mais provável.
    Se estiver duvidoso, retorna None.
    """

    if not scores:
        return None

    maior = max(scores)
    ordenados = sorted(scores, reverse=True)

    if maior < limite_minimo:
        return None

    if len(ordenados) > 1 and ordenados[0] - ordenados[1] < diferenca_minima:
        return None

    return int(np.argmax(scores))


def ler_numero_aluno(image, thresh, bubbles):
    """
    Lê número do aluno no novo modelo.

    Estratégia:
    - usa os contornos detectados para descobrir as 2 colunas;
    - infere as 10 linhas da tabela;
    - lê todas as posições esperadas.
    """

    bolhas_aluno = []

    for (x, y, w, h) in bubbles:
        if 70 < x < 190 and 130 < y < 410:
            bolhas_aluno.append((x, y, w, h))

    print(f"Bolhas aluno: {len(bolhas_aluno)}")

    xs = []
    ys = []

    for (x, y, w, h) in bolhas_aluno:
        xs.append(x + w / 2)
        ys.append(y + h / 2)

    colunas_x = clusterizar_valores(xs, tolerancia=18)
    colunas_x = sorted(colunas_x)

    if len(colunas_x) > 2:
        # pega as duas colunas mais à esquerda dentro da região
        colunas_x = colunas_x[:2]

    linhas_y = clusterizar_valores(ys, tolerancia=10)
    linhas_y = inferir_linhas_regulares(linhas_y, quantidade=10)

    print("Colunas aluno:", colunas_x)
    print("Linhas aluno:", linhas_y)

    numero = ""

    for idx_coluna, x_centro in enumerate(colunas_x, start=1):
        scores = []

        for y_centro in linhas_y:
            score = score_bolha(
                image=image,
                thresh=thresh,
                x_centro=x_centro,
                y_centro=y_centro,
                raio=4,
            )

            scores.append(score)

        print(f"Scores aluno coluna {idx_coluna}:", scores)

        digito = escolher_marcacao(
            scores,
            limite_minimo=0.35,
            diferenca_minima=0.12,
        )

        if digito is None:
            numero += "?"
        else:
            numero += str(digito)

    return numero


def processar_respostas(image, thresh, bubbles):
    """
    Lê as respostas no novo modelo.

    Estratégia:
    - usa bolhas detectadas para descobrir a grade;
    - infere 8 linhas e 5 colunas;
    - lê todas as 40 posições esperadas.
    """

    bolhas_questoes = []

    for (x, y, w, h) in bubbles:
        if 270 < x < 520 and 130 < y < 410:
            bolhas_questoes.append((x, y, w, h))

    print(f"Bolhas questões: {len(bolhas_questoes)}")

    xs = []
    ys = []

    for (x, y, w, h) in bolhas_questoes:
        xs.append(x + w / 2)
        ys.append(y + h / 2)

    colunas_x = clusterizar_valores(xs, tolerancia=18)
    colunas_x = sorted(colunas_x)

    if len(colunas_x) > 5:
        colunas_x = colunas_x[:5]

    linhas_y = clusterizar_valores(ys, tolerancia=10)
    linhas_y = inferir_linhas_regulares(linhas_y, quantidade=8)

    print("Colunas questões:", colunas_x)
    print("Linhas questões:", linhas_y)

    respostas = []

    for idx_linha, y_centro in enumerate(linhas_y, start=1):
        scores = []

        for x_centro in colunas_x:
            score = score_bolha(
                image=image,
                thresh=thresh,
                x_centro=x_centro,
                y_centro=y_centro,
                raio=4,
            )

            scores.append(score)

        print(f"Scores questão {idx_linha}:", scores)

        marcada = escolher_marcacao(
            scores,
            limite_minimo=0.35,
            diferenca_minima=0.12,
        )

        if marcada is None:
            respostas.append(None)
        else:
            respostas.append(LETRAS[marcada])

    return respostas


def calcular_nota(respostas, gabarito):
    nota = 0

    for i in range(min(len(respostas), len(gabarito))):
        if respostas[i] == gabarito[i]:
            nota += 1

    return nota


def salvar_debug(image, thresh, bubbles):
    debug_img = image.copy()

    for i, (x, y, w, h) in enumerate(bubbles):
        cv2.rectangle(
            debug_img,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2,
        )

        cv2.putText(
            debug_img,
            str(i),
            (x, y - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (0, 0, 255),
            1,
        )

    cv2.imwrite("debug_resultado.jpg", debug_img)
    cv2.imwrite("debug_threshold.jpg", thresh)

    # cv2.imshow("Bubbles Detectadas", debug_img)
    # cv2.imshow("Threshold", thresh)

    # cv2.waitKey(0)
    # cv2.destroyAllWindows()


def process_image(path, gabarito=None):
    raw_image = cv2.imread(path)

    if raw_image is None:
        raise ValueError(f"Imagem não encontrada: {path}")

    image = cv2.resize(raw_image, (IMAGE_WIDTH, IMAGE_HEIGHT))

    image, thresh = preprocess_image_from_array(image)

    bubbles = find_bubbles(thresh)

    print(f"Encontrou {len(bubbles)} bolhas (antes do filtro)")

    h_img, w_img = thresh.shape

    filtered = []

    for (x, y, w, h) in bubbles:
        if x < 20 or y < 20 or x > w_img - 20 or y > h_img - 20:
            continue

        filtered.append((x, y, w, h))

    bubbles = filtered

    print(f"Após filtro de borda: {len(bubbles)} bolhas")

    numero_aluno = ler_numero_aluno(image, thresh, bubbles)
    print("Número do aluno:", numero_aluno)

    respostas = processar_respostas(image, thresh, bubbles)
    print("Respostas:", respostas)

    # Gabarito correto informado por você
    if gabarito is None:
        gabarito = ["A", "A", "C", "B", "E", "D", "D", "A"]

    nota = calcular_nota(respostas, gabarito)

    print(f"Nota: {nota}/{len(gabarito)}")

    salvar_debug(image, thresh, bubbles)

    return {
        "numero_aluno": numero_aluno,
        "respostas": respostas,
        "total": len(respostas),
        "nota": nota,
    }