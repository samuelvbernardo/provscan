# ProvScan API

API para criação de provas, geração de cartões-resposta e correção automática de gabaritos por imagem, construída com Django, Django REST Framework e OpenCV.

## Tecnologias

- Python 3.13
- Django 5.2
- Django REST Framework
- SimpleJWT
- drf-spectacular
- PostgreSQL / Supabase
- OpenCV, Pillow
- ReportLab
- Gunicorn, WhiteNoise
- Docker

## Funcionalidades principais

- Autenticação via JWT
- Cadastro de turmas e alunos
- Criação de provas com definição de quantidade de questões e alternativas
- Cadastro do gabarito oficial
- Geração automática do cartão-resposta em PDF
- Upload da imagem do cartão preenchido e leitura automática do número do aluno e respostas
- Identificação de questões em branco ou dupla marcação
- Correção automática e histórico de resultados

## Requisitos

- Docker
- Docker Compose

## Configuração do ambiente

Crie um arquivo `.env` dentro da pasta `scan_api` (no mesmo nível da `.env.example`) com as variáveis necessárias.

## Executando com Docker

Na pasta que contém o `docker-compose.yml`:

```bash
docker compose up --build
```

A aplicação ficará disponível em:

- Aplicação: http://127.0.0.1:8000
- Documentação da API: http://127.0.0.1:8000/api/docs/
- Painel administrativo: http://127.0.0.1:8000/admin/

### Criar superusuário

Com os containers em execução:

```bash
docker compose exec backend python manage.py createsuperuser
```

### Migrations

As migrations são aplicadas automaticamente no `entrypoint.sh`. Para executar manualmente:

```bash
docker compose exec backend python manage.py migrate
```

### Coletar arquivos estáticos

Executado automaticamente no `entrypoint.sh`. Para executar manualmente:

```bash
docker compose exec backend python manage.py collectstatic --noinput
```

### Parar containers

```bash
docker compose down
```

## Estrutura da API

### Autenticação (JWT)

POST /api/token/

Request (JSON):

```json
{
  "username": "seu_usuario",
  "password": "sua_senha"
}
```

Resposta:

```json
{
  "refresh": "...",
  "access": "..."
}
```

Para acessar rotas protegidas, inclua o header:

Authorization: Bearer SEU_ACCESS_TOKEN

### Rotas principais

Turmas (class-groups)

```
GET    /api/v1/class-groups/
POST   /api/v1/class-groups/
GET    /api/v1/class-groups/{id}/
PUT    /api/v1/class-groups/{id}/
PATCH  /api/v1/class-groups/{id}/
DELETE /api/v1/class-groups/{id}/
```

Exemplo de criação (JSON):

```json
{
  "name": "5 Ano A",
  "school_year": "5º ano",
  "is_active": true
}
```

Alunos (students)

```
GET    /api/v1/students/
POST   /api/v1/students/
GET    /api/v1/students/{id}/
PUT    /api/v1/students/{id}/
PATCH  /api/v1/students/{id}/
DELETE /api/v1/students/{id}/
```

Listar por turma:

```
GET /api/v1/students/?class_group=1
```

Exemplo de criação (JSON):

```json
{
  "class_group": 1,
  "number": 25,
  "name": "Sabrina Vilar",
  "is_active": true
}
```

Provas (exams)

```
GET    /api/v1/exams/
POST   /api/v1/exams/
GET    /api/v1/exams/{id}/
PUT    /api/v1/exams/{id}/
PATCH  /api/v1/exams/{id}/
DELETE /api/v1/exams/{id}/
```

Exemplo de criação (JSON):

```json
{
  "title": "Prova de Matemática - 5 Ano A",
  "description": "Avaliação bimestral de matemática",
  "class_group": 1,
  "questions_count": 15,
  "options_count": 4,
  "answer_key": ["A","B","C","D","A","B","C","D","A","B","C","D","A","B","C"],
  "is_active": true
}
```

Ao criar uma prova o sistema gera automaticamente o PDF do cartão-resposta no campo `template_file`.

Resultados (scan-results)

```
GET /api/v1/scan-results/
GET /api/v1/scan-results/{id}/
```

Exemplo de resposta:

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "exam": 1,
      "exam_title": "Prova de Matemática - 5 Ano A",
      "student": 3,
      "student_name": "Sabrina Vilar",
      "student_identified": true,
      "student_number": "25",
      "answers": ["A","B","C","D"],
      "score": 4,
      "total_questions": 4,
      "image": "http://127.0.0.1:8000/media/scan_results/gabarito.jpg",
      "warnings": [],
      "created_at": "2026-05-02T00:00:00-03:00",
      "updated_at": "2026-05-02T00:00:00-03:00"
    }
  ]
}
```

Possíveis avisos no campo `warnings`:

- "Existem questões em branco ou com dupla marcação: [9, 21]."
- "O número do aluno foi lido, mas nenhum aluno correspondente foi encontrado na turma da prova."
- "Não foi possível identificar corretamente o número do aluno."

---

Para detalhes de uso e dos endpoints consulte a documentação em /api/docs.