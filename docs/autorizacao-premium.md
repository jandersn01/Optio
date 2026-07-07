# Autorização por papel: grupo **Premium**

Este documento explica **como a autorização por papel foi implementada** no projeto e
**como configurá-la no painel admin do Django**.

## 1. Visão geral

O projeto tem dois tipos de autorização:

- **Por dono (ownership):** cada usuário só acessa os próprios dados
  (`SearchRequest.objects.for_user(user)`, `get_object_or_404(..., user=request.user)`, etc.).
- **Por papel (RBAC):** benefícios concedidos conforme o **grupo** a que o usuário pertence.
  É o que este documento cobre.

O papel **Premium** é modelado como um **Grupo nativo do Django** (`django.contrib.auth.models.Group`).
Quem está no grupo `Premium` ganha um **limite maior de alertas ativos**.

| Papel            | Limite de alertas ativos            | Variável de ambiente          |
|------------------|-------------------------------------|-------------------------------|
| Comum (padrão)   | `3`                                 | `MAX_ACTIVE_ALERTS_PER_USER`  |
| Premium          | `20`                                | `PREMIUM_MAX_ACTIVE_ALERTS`   |

## 2. Como foi implementado

A responsabilidade foi separada por domínio (Clean Architecture): o app **`core`** decide
*quem é premium*; o app **`search`** decide *quais são os limites*.

### 2.1. `core` — quem é premium (domínio do usuário)

`app/core/models.py` — o papel é um atributo do próprio usuário. O nome do grupo fica
encapsulado numa constante, então se amanhã "premium" virar um campo/plano, muda-se só aqui.

```python
class CustomUser(AbstractUser):
    # Grupo (papel) que concede benefícios de plano Premium
    PREMIUM_GROUP = 'Premium'

    # ... demais campos ...

    @property
    def is_premium(self) -> bool:
        """True se o usuário pertence ao grupo Premium."""
        return self.groups.filter(name=self.PREMIUM_GROUP).exists()
```

### 2.2. Migração — cria o grupo automaticamente

`app/core/migrations/0007_create_premium_group.py` garante que o grupo `Premium`
exista em qualquer ambiente (idempotente e reversível):

```python
def create_premium_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name='Premium')
```

### 2.3. `search` — os limites (domínio de alertas)

`app/search/services.py` conhece apenas os **números** e pergunta ao usuário se ele é premium,
sem saber *como* isso é determinado:

```python
FREE_MAX_ACTIVE_ALERTS = int(os.getenv("MAX_ACTIVE_ALERTS_PER_USER", "3"))
PREMIUM_MAX_ACTIVE_ALERTS = int(os.getenv("PREMIUM_MAX_ACTIVE_ALERTS", "20"))

def max_active_alerts_for(user) -> int:
    """Limite de alertas ativos conforme o papel do usuário."""
    return PREMIUM_MAX_ACTIVE_ALERTS if user.is_premium else FREE_MAX_ACTIVE_ALERTS
```

`max_active_alerts_for(user)` é usado em `create_alert_from_search` e `toggle_alert`
(checagem do limite) e nas views (mensagens que mostram o limite do usuário).

## 3. Como configurar no painel admin do Django

### Pré-requisitos

1. Rodar as migrações (cria o grupo `Premium`):
   ```bash
   docker compose run --rm web python manage.py migrate
   ```
2. Ter um superusuário para acessar o admin. Para criar um:
   ```bash
   docker compose run --rm web python manage.py createsuperuser
   ```
   Para promover uma conta existente a superusuário:
   ```bash
   docker compose run --rm web python manage.py shell -c "
   from django.contrib.auth import get_user_model
   U = get_user_model()
   u = U.objects.get(email='SEU_EMAIL@exemplo.com')
   u.is_staff = True; u.is_superuser = True
   u.save(update_fields=['is_staff', 'is_superuser'])
   print('OK', u.email)
   "
   ```

### Passo a passo (admin)

1. Acesse `http://localhost:8000/admin/` e faça login com o superusuário.
2. Vá em **Usuários** e clique no usuário que receberá o papel.
3. Na seção **Permissões**, localize o campo **Grupos**.
4. Selecione **Premium** e mova para "Grupos escolhidos".
5. Clique em **Salvar**.

O efeito é imediato: na próxima ação do usuário, `is_premium` retorna `True` e o limite
de alertas ativos passa a ser o Premium (20 por padrão).

> Observação de segurança: colocar alguém no grupo **Premium** concede apenas o benefício
> de plano — **não** dá acesso ao admin. Acesso ao admin exige `is_staff=True`; controle
> total exige `is_superuser=True`. Reserve esses dois para administradores.

### Alternativa via linha de comando

```bash
docker compose run --rm web python manage.py shell -c "
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
U = get_user_model()
u = U.objects.get(email='aluno@exemplo.com')
u.groups.add(Group.objects.get(name='Premium'))
print(u.email, 'premium:', u.is_premium)
"
```

## 4. Configuração dos limites

Definidos por variável de ambiente (veja `.env.example`):

```env
MAX_ACTIVE_ALERTS_PER_USER=3   # limite do usuário comum
PREMIUM_MAX_ACTIVE_ALERTS=20   # limite do usuário Premium
```

## 5. Como estender para outros papéis

O mesmo esqueleto serve para novos papéis (ex.: "Moderador"):

1. Criar um grupo (via migração ou admin) e uma propriedade `is_<papel>` no `CustomUser`.
2. Aplicar a regra onde ela pertence: numa view/serializer (web) ou numa
   *permission class* do DRF (API), checando o grupo.
