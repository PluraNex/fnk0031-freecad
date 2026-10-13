# Validação do CAD V3 provisório

## Concluído e verificado

- Seis perfis oficiais com 74, 106, 14, 13, 64 e 49 entidades, respectivamente AC01–AC06. Recortes, rasgos e furos incluídos. O arquivo preliminar antigo não tinha os rasgos dos chassis; foi preservado e substituído funcionalmente pela biblioteca nova.
- Contornos exportados fechados por verificação de incidência de extremidades a 0,00001 mm; handles únicos por peça. DXF reaberto com INSUNITS=4 e sem erros de auditoria. SVG usa as mesmas linhas, arcos e círculos, unidades físicas mm, sem escala adicional.
- Seis Pads com um sólido válido cada. Área do perfil calculada independentemente pelos contornos fonte comparada com volume/espessura: maior diferença inferior a 0,000001 mm². Nenhuma compensação de corte.
- STEP individuais reimportados válidos, um sólido por peça; diferença máxima de volume inferior a 0,000000002 mm³. STEP do inventário contém 26 sólidos válidos. A espessura 3 mm destes arquivos é APENAS visual.
- Biblioteca 2D e arquivo 3D fechados e reabertos, recompute sem objetos inválidos. Os 26 vínculos são internos ao documento.
- Cópia paramétrica alterada de 3 para 4 mm: seis sólidos válidos, razão de volumes 4/3 dentro de 0,00000001; 26 vínculos atualizados. O nominal visual permanece 3 mm.
- Modelo analítico baseado diretamente em FNHRBasic.cpp CalculatePoint: primeira perna testada em três trios de ângulos contra cálculo independente; erro de ponta inferior a 0,000001 mm. Só depois foram criadas as outras cinco. Segmentos e=55 e f=70 mm conferidos. São 18 parâmetros angulares, não uma prova de 18 graus de liberdade de juntas mecânicas.
- PDF TechDraw exportado e renderizado para inspeção das seis páginas. A primeira exportação estava vazia antes da renderização Qt; foi corrigida abrindo as páginas no FreeCAD e reexportando. As páginas entregues mostram os perfis e avisos provisórios. São pranchas de perfil, ainda sem todas as cotas funcionais de fabricação.

Resultados detalhados nos arquivos validacao_pecas_3D.json, validacao_vetores.json, validacao_STEP.json, validacao_parametrica.json, validacao_reabertura.json e validacao_cinematica.json.

## Limites da validação

A concordância acima é com o vetor V3 consultado, não com medição do kit físico. Espessura e interfaces comerciais desconhecidas impedem aprovação da montagem. Nenhum estudo de colisões completo, passagem de cabos ou tolerância foi executado. As peças não foram liberadas para fabricação. Massa, torque, carga e desempenho não foram calculados.

Os corpos de biblioteca e o inventário de peças são entregues; a montagem completa, ferragens/eletrônica/servos e remoto, configurações físicas de instalação/calibração e vista explodida da montagem permanecem pendentes. Não há juntas Assembly nativas: sua API instalada foi inspecionada, mas criar juntas sem as interfaces confirmadas daria uma validação enganosa. O arquivo cinemático é explicitamente um modelo analítico separado.

As fontes foram consultadas sem inventar valores ausentes. A divergência do organizador de cabos permanece: 750 mm no PDF, 500 mm na documentação online.
