# FNK0031 — biblioteca CAD V3 provisória

**Atualização:** a montagem inicial com aproximações autorizadas agora está em `FNK0031_V3_Montagem_Inicial.FCStd`. Consulte `montagem_inicial/LEIA-ME-MONTAGEM.md`. As limitações abaixo descrevem a entrega anterior da biblioteca, preservada como referência; o robô completo já foi representado como conjunto inicial provisório.

Atualizado em 12/10/2026. Trabalho sem gravação, conforme solicitado.

## Abrir

- **FNK0031_V3_Visualizacao_3D.FCStd**: seis peças acrílicas mestres com Sketcher + PartDesign Pad, planilha Parameters, 26 instâncias App::Link no grupo Kit26 e seis páginas TechDraw. O grupo Kit26 é um inventário espacial de peças separadas, NÃO uma montagem do robô.
- **FNK0031_V3_Biblioteca_2D.FCStd**: seis perfis completos extraídos do DWG V3, sem espessura presumida. Contém os rasgos dos chassis que faltavam na versão preliminar anterior.
- **FNK0031_V3_Cinematica.FCStd**: esqueleto analítico de seis pernas, com 18 ângulos editáveis e expressões nativas. Não contém servos nem juntas mecânicas resolvidas.

Os documentos são independentes: os App::Link do inventário apontam para mestres no próprio documento; os desenhos referenciam os próprios esboços. Não exigem macros para abrir ou recomputar. Não habilitar macros para apenas consultar estes arquivos.

## Editar o 3D

Em Parameters, B2/VisualThickness controla todos os Pads. **3 mm é apenas uma escolha de visualização; a espessura real continua desconhecida.** Não fabricar a partir do STEP sem resolver essa dimensão e as interfaces.

Cada Body AC01–AC06 tem Profile e Pad. Os perfis preservam linhas, arcos e círculos oficiais por restrições Block. Estão totalmente restringidos, mas não constituem esboços redesenhados com intenção dimensional: para modificar um contorno, remova/edite os bloqueios pertinentes numa cópia e trate o resultado como revisão derivada.

Mostre Kit26 e oculte os seis Bodies mestres para visualizar as 26 instâncias sem duplicação visual. Para voltar à biblioteca, oculte Kit26 e mostre os Bodies. As posições desse inventário não são posições de montagem.

No estudo cinemático, edite Alpha/Beta/Gamma de Leg1Angles…Leg6Angles. Os segmentos recalculam por expressões nativas; comprimentos e origens vêm de KinematicParameters. A postura salva é demonstrativa. Os limites do firmware estão no CSV e NÃO são limites mecânicos validados nem são impostos pelas expressões.

## Entregáveis

- 3D_provisorio: STEP individual, biblioteca de seis peças e inventário de 26 peças; imagens gerais.
- perfis_1a1: seis DXF R2013 e seis SVG, unidades mm, escala 1:1, somente geometria de corte; nenhum kerf aplicado.
- desenhos/FNK0031_V3_Perfis_TechDraw.pdf: seis páginas A4 em escala 1:1, **pranchas de perfil provisórias**, não desenhos completos de fabricação. Imprimir em tamanho real, sem ajustar à página.
- furos_rastreaveis.csv: diâmetros e centros locais com handles do DWG. Origem local no mínimo XY do contorno externo; sem rotação ou escala.
- BOM_V3.csv: quantidades do inventário; consumo e sobressalentes comerciais desconhecidos ficam explícitos.
- parametros.json, firmware-joints.csv, validacao_*.json: fontes, parâmetros, limites de software e resultados numéricos.
- checkpoints: etapas recuperáveis e cópia usada no teste de 4 mm. **Essa cópia não é o nominal entregue.**
- backups: versões preservadas antes de substituir arquivos.

## Construção reproduzível

Scripts usam ROOT/BASE para esta pasta; ajuste esse caminho se transportar a biblioteca. Pelo MCP execute o conteúdo de rebuild_profiles.py e chame rebuild_profile(0)…rebuild_profile(5), um estágio por chamada. Esse script altera apenas seu documento FNK0031_Rebuild. Depois carregue build_library_3d.py, chame init_preview(), make_part(0)…make_part(5) e finish_library(). Carregue build_drawings.py, chame drawing(0)…drawing(5), e em chamada posterior export_drawings() para aguardar a renderização Qt. kit_layout() cria/atualiza as instâncias. export_vectors.py roda pelo Python do FreeCAD com ezdxf localizado no caminho indicado. build_kinematics.py fornece init_kinematics(), make_kinematic_leg(1)…(6), finish_kinematics(), usando safe_save do script da biblioteca.

Os mestres e instâncias usam IDs estáveis. O teste de reexecução atualizou os seis Bodies sem duplicá-los. Os scripts não devem ser executados simultaneamente. preserve sempre alterações manuais antes de reconstruir.

## Fontes e estado

Geometria: DWG oficial FNK0031 V3, commit 1596c5ffe07a262fa7dc6d0189de6c2321270278, convertido com LibreDWG 0.14.8608. Original em research/freenove-official/Hardware; DXF e auditoria em audit_20261012. Unidades INSUNITS=4, mm. Nenhum desenho do FNK0052 foi empregado.

Fabricante: https://github.com/Freenove/Freenove_Hexapod_Robot_Kit
Montagem: https://docs.freenove.com/projects/fnk0031/en/latest/fnk0031/codes/tutorial/Assembly.html
Inventário: https://docs.freenove.com/projects/fnk0031/en/latest/fnk0031/codes/tutorial/List.html
Licença publicada nas fontes: CC BY-NC-SA 3.0. Fontes originais preservadas.

V3 foi autorizada como provisória. Compra em 21/04/2023 e identificação da caixa não confirmam a revisão física. A variante comprada inclui controle remoto, ainda não reconstruído dimensionalmente.

**Ainda não é uma reprodução fiel completa do robô.** Faltam espessura real, identificação/envelope/abas/eixo/spline do servo, braço circular, registro das interfaces em Z, placas eletrônicas e remoto, ferragens detalhadas e tolerâncias. Não foram validados montagem física de uma perna, orientações finais, interferências, cabos, folgas, carga ou dinâmica. Não há vista explodida de uma montagem resolvida; o inventário separado não deve ser interpretado como tal.

Esses dados não foram encontrados nas fontes oficiais examinadas. Nenhum SG90/MG90S/MG996R foi atribuído por aparência. As próximas confirmações indispensáveis são inscrição da placa, espessura sem película, identificação/datasheet do servo e suas interfaces, ou desenho mecânico do fabricante contendo essas informações.
