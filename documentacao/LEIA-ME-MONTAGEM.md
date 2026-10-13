# FNK0031 — montagem inicial completa para conferência

Esta entrega substitui a limitação de escopo da biblioteca anterior. O usuário autorizou construir o conjunto inicial com aproximações registradas, para ajustar depois com paquímetro.

## Arquivo principal

Abra **../FNK0031_V3_Montagem_Inicial.FCStd**. Está salvo na vista isométrica do robô montado. O documento é autocontido; seus vínculos são internos. Os arquivos anteriores foram preservados.

- Robot: chassis, seis pernas, 18 servos genéricos, 18 braços circulares, ferragens, controlador, WLAN, conectores, duas baterias e cabos ilustrativos.
- Library: mestres das peças, normalmente ocultos. As 26 instâncias acrílicas usam os seis perfis DWG oficiais. A espessura continua provisória em 3 mm.
- Dimensions: medidas centrais para atualização. As descrições das propriedades indicam origem e estado.
- Exploded: vista explodida ilustrativa. Para vê-la, oculte Robot e mostre Exploded. Não representa uma sequência comprovada de desmontagem.
- Remote: representação inicial separada do controle da variante comprada. Está oculta por padrão; oculte Robot, mostre Remote e enquadre tudo. Seu envelope, controles e placa são genéricos, não reconstrução dimensional confirmada do controle físico.

Os servos não receberam identificação comercial presumida. O corpo, abas, eixo liso, braço e parafuso central formam um modelo genérico. Não foram desenhados dentes do spline nem roscas helicoidais.

## Como corrigiremos pelas suas medidas

Envie o nome da peça, a medida e os pontos entre os quais mediu. A tabela **medir_com_paquimetro.csv** organiza as primeiras medidas úteis; **incertezas_e_medidas.json** guarda os mesmos valores e a origem de cada um. Os envelopes secundários estão em **componentes_secundarios.csv**.

Prioridade sugerida: espessura do acrílico; largura/comprimento/altura do corpo do servo; distância entre furos das abas; posição/altura do eixo; diâmetro e espessura do braço circular; distância entre chassis; envelope da placa. Não é necessário medir tudo de uma vez.

As alterações serão feitas em Dimensions e aplicadas por etapas com o script de construção. Os Pads das peças acrílicas respondem diretamente à espessura. As demais geometrias comerciais e posições precisam executar novamente os estágios pertinentes — não basta apertar Recompute para reconstruir todos os envelopes.

Para atualização integral manual, use **../Atualizar_Montagem.FCMacro**. Ela executa a reconstrução em etapas pelo timer Qt e grava checkpoints; não fecha os outros documentos. O caminho do script dentro da macro deve ser ajustado se a pasta mudar. Abrir ou consultar o FCStd não exige executar a macro.

Os ângulos Alpha/Beta/Gamma de cada Leg são entradas para posicionamento pelo script make_leg(n). As distâncias A/B/C e comprimento de ligação vêm do firmware; o registro físico dos planos dos servos permanece provisório. Esta montagem usa posicionamentos calculados, não juntas Assembly resolvidas. O estudo cinemático separado permanece disponível no arquivo anterior.

## Verificação executada

- 26 instâncias acrílicas, 18 servos e 18 braços circulares conferidos pela árvore.
- 36 parafusos M2x10 e 36 porcas M2, 72 autorroscantes M1.2x7, seis parafusos M3x12 e seis porcas M3, oito M3x8, quatro espaçadores M3x27 e quatro M3x5 representados. Também há 18 parafusos de eixo de dimensão presumida. Consumo é uma hipótese de montagem, não inventário físico certificado.
- As seis ligações mantêm 55 mm entre eixos; a referência cinemática terminal é 70 mm. As pontas geométricas seguem o contorno original e o registro provisório do servo.
- STEP do robô reimportado: 411 sólidos geométricos válidos, mesma contagem do conjunto exportado e diferença de volume inferior a 0,00000001 mm³. Essa contagem inclui subdivisões de componentes e segmentos de cabo; não é a quantidade de peças da BOM.
- FCStd fechado e reaberto, sem objetos inválidos. Vínculos internos confirmados.
- Cópia de teste: espessura de 3 para 3,2 mm atualizou o Pad; largura do servo de 12 para 13 mm reconstruiu seu envelope; Beta da perna 1 de 90 para 95 graus deslocou o eixo C em aproximadamente 4,7981 mm. O nominal entregue foi preservado.
- Interferências amostradas registradas em interferencias_amostradas.json. As interfaces servo/suporte têm sobreposição aproximada de 2,295 mm³ na representação genérica. Serão revistas com as medidas. Não foi feita validação completa de colisões, cabos ou movimento.

## Aproximações importantes

Além das medidas da tabela, orientação fina das abas/suportes, alturas das interfaces, detalhes da eletrônica, cabeças de fixadores, posição dos conectores, percurso dos cabos e o controle remoto são simplificados. Não se deve atribuir precisão ao detalhe visual. Folgas, spline, tolerâncias, carga e torque não foram confirmados.

O modelo está completo como **conjunto inicial de visualização e ajuste**, não como reprodução dimensional aprovada ou arquivo liberado para fabricação. Isso não interrompe a construção: as incertezas agora são itens de correção do modelo existente.

## Fontes

Perfis: DWG V3 oficial, commit 1596c5ffe07a262fa7dc6d0189de6c2321270278. Montagem orientada pelas ilustrações do Tutorial_for_V3.pdf, em particular páginas 42, 49, 50 e 52. Cinemática: FNHRBasic.cpp. Revisão V3 provisória autorizada; identificação física ainda a confirmar. Repositório: https://github.com/Freenove/Freenove_Hexapod_Robot_Kit . Licença das fontes: CC BY-NC-SA 3.0.

## Arquivos

FNK0031_robo_PROVISORIO.step; Controle_envelope_PROVISORIO.step; robo_isometrico.png; robo_superior.png; robo_frontal.png; robo_lateral.png; explodida.png; controle_provisorio.png; registros CSV/JSON e este documento.
