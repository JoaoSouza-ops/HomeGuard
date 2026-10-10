# Guia de Contribuição — HomeGuard

Este documento define como a equipe trabalha no repositório. Ele existe para cumprir (de verdade, não só no papel) o requisito de "colaboração open source real" do edital.

## 1. Fluxo de branches (GitHub Flow)

```
main            → sempre estável, sempre "deployável"
feature/xxxxx   → uma branch por tarefa
```

Passo a passo:
1. Sincronizar com a `main`: `git checkout main && git pull`
2. Criar a branch: `git checkout -b feature/nome-curto-da-tarefa`
3. Commitar em pequenos incrementos (ver padrão abaixo).
4. Subir a branch: `git push origin feature/nome-curto-da-tarefa`
5. Abrir um Pull Request no GitHub, preenchendo o template.
6. **Pelo menos 1 outro integrante precisa revisar e aprovar antes do merge.**
7. Merge feito, apagar a branch.

> A `main` deve ter **branch protection** ativada (Settings → Branches): exigir PR, exigir pelo menos 1 aprovação, exigir que o CI passe.

## 2. Padrão de commits (Conventional Commits)

```
<tipo>: <descrição curta no imperativo>

tipos permitidos:
feat:     nova funcionalidade
fix:      correção de bug
docs:     mudança só de documentação
test:     adição/ajuste de testes
chore:    tarefas de manutenção (deps, configs)
refactor: mudança de código sem alterar comportamento
```

Exemplos:
```
feat: adiciona endpoint GET /devices
fix: corrige cálculo de score quando pesos somam zero
docs: atualiza contrato da API com endpoint de mitigação
```

## 3. Template de Pull Request

Ao abrir um PR, incluam:
```markdown
## O que este PR faz
(descrição breve)

## Como testar
(passos para o revisor rodar e validar localmente)

## Checklist
- [ ] Testes adicionados/atualizados
- [ ] Documentação em `docs/` atualizada, se aplicável
- [ ] CI passando
```

## 4. Regras de code review

Quem revisa deve checar:
- O código faz o que o PR descreve?
- Há testes cobrindo a mudança?
- O contrato da API (`docs/03-BACKEND-API.md`) foi respeitado, se aplicável?
- Alguma credencial ou segredo foi commitado por engano?

Quem recebe a revisão:
- Responder a todos os comentários (mesmo que só com "feito" ou explicando por que discorda).
- Não fazer merge do próprio PR.

## 5. Versionamento semântico

Usaremos tags no formato `vMAJOR.MINOR.PATCH`:
- `MAJOR`: mudança incompatível na API.
- `MINOR`: nova funcionalidade compatível com versões anteriores.
- `PATCH`: correção de bug.

Criar uma tag ao final de cada semana de integração relevante (ex: `v0.1.0` ao final da Semana 2, `v0.2.0` ao final da Semana 4, etc — ver `docs/08-CRONOGRAMA-PAPEIS.md`).

```bash
git tag -a v0.1.0 -m "Contratos de API e fundações do projeto"
git push origin v0.1.0
```

## 6. Licença

Este projeto usa a licença **[MIT / Apache 2.0 / GPL — confirmar com a equipe e atualizar aqui e no arquivo LICENSE]**.
