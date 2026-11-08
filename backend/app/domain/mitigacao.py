import ipaddress
import logging

logger = logging.getLogger(__name__)

# Porta usada por "bloquear_porta": a do Telnet, a vulnerabilidade do projeto
# (docs/06-SEGURANCA.md). O MitigacaoRequest ainda não tem um campo de porta.
PORTA_TELNET = 23

# MODO SIMULADO: nenhuma função aqui executa comando de sistema. Elas validam os
# dados e registram no log o que seria feito. Quando a mitigação real entrar
# (iptables, só em Linux), ela deve reaproveitar estas validações.


def _validar_ip(ip: str) -> None:
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        raise ValueError(f"IP inválido: {ip!r}") from None


def _validar_porta(porta: int) -> None:
    if not 1 <= porta <= 65535:
        raise ValueError(f"Porta inválida: {porta}")


def bloquear_porta(ip: str, porta: int) -> None:
    _validar_ip(ip)
    _validar_porta(porta)
    logger.warning("[SIMULADO] bloquear a porta %s do IP %s (nenhum comando foi executado)", porta, ip)


def bloquear_ip(ip: str) -> None:
    _validar_ip(ip)
    logger.warning("[SIMULADO] bloquear o IP %s (nenhum comando foi executado)", ip)


def executar_mitigacao(acao: str, ip: str) -> None:
    """Executa (de forma simulada) a ação pedida contra o IP do dispositivo.

    Levanta ValueError se a ação não for suportada ou se o IP for inválido.
    """
    if acao == "bloquear_porta":
        bloquear_porta(ip, PORTA_TELNET)
    elif acao == "bloquear_ip":
        bloquear_ip(ip)
    else:
        raise ValueError(f"Ação não suportada: {acao!r} (use 'bloquear_porta' ou 'bloquear_ip')")
