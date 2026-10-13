# FNK0031 no FreeCAD — estudo em desenvolvimento

> **Em desenvolvimento.** Modelo derivado de referências públicas da versão V3. A geometria das chapas vem do DWG oficial, mas a revisão física do kit do autor ainda será confirmada. Espessura de 3 mm, servos, fixações, eletrônica e folgas são provisórios. Não usar os arquivos como instrução de fabricação final.

Este repositório reúne a modelagem original do hexápode no FreeCAD **sem as carenagens experimentais**. A sequência documentada vai dos seis perfis do acrílico à montagem inicial das seis pernas e ao controle cinemático. É um registro aberto de trabalho, feito para ser corrigido com medições do robô físico.

## Por onde começar

1. Abra `cad/FNK0031_V3_Movimento.FCStd` no FreeCAD 1.1. O arquivo abre sem executar macro.
2. Para inspecionar os controles, use a cópia em `controle-freecad/FNK0031_V3_Movimento.FCStd` e execute `controle-freecad/Iniciar_Movimento.FCMacro`. Mantenha essa pasta inteira junta: a macro usa `movimento/` e `firmware-joints.csv` por caminhos relativos.
3. Para estudar as peças, abra `cad/FNK0031_V3_Visualizacao_3D.FCStd`; para o esqueleto matemático separado, abra `cad/FNK0031_V3_Cinematica.FCStd`.
4. Consulte `documentacao/LEIA-ME-CONTROLE.md` para os modos de marcha, o teste de colisões e os limites.

## Organização

| Pasta | Conteúdo |
|---|---|
| `cad/` | Cinco documentos nativos FreeCAD: perfis, biblioteca 3D, cinemática, montagem inicial e movimento. |
| `exportacoes/perfis-2d/` | Seis DXF e SVG em mm, mais pranchas PDF. Não há compensação de corte. |
| `exportacoes/step/` | Seis chapas 3D e robô completo em STEP, com medidas provisórias. |
| `impressao-3d/stl-prototipo/` | Seis STLs fechados das chapas AC01–AC06, gerados com espessura visual de 3 mm. Apenas prototipagem e conferência. |
| `imagens/` | Vistas do FreeCAD e capa editorial ilustrativa. A capa não é uma captura técnica. |
| `dados/` e `documentacao/` | BOM, limites, validações, interferências amostradas e planilha de medidas futuras. |
| `controle-freecad/` | Macro e código do painel cinemático. |

## Impressão 3D experimental

As peças AC01–AC06 foram concebidas como chapas de acrílico cortadas a laser. Os STLs reproduzem uma extrusão visual de 3 mm dos perfis; **não foram adaptados para impressão nem testados no robô físico**. Antes de imprimir para montagem, confirme espessura, folga dos furos, orientação, resistência do material, suporte de impressão e distâncias reais dos servos. Comece por uma peça de teste e compare com o kit físico.

## O que foi verificado

- Seis perfis rastreados ao DWG V3 e 26 instâncias acrílicas na biblioteca.
- Seis sólidos CAD válidos e exportações STEP reimportadas.
- Montagem visual inicial com 18 servos genéricos e seis pernas; arquivo reaberto e recomputado.
- Controle matemático com nove modos e 48.762 posições de pernas verificadas numericamente.
- Testes de interferência em poses amostradas registraram possíveis colisões; não há certificação de percurso livre, força, torque ou estabilidade dinâmica.

## Fontes e licença

Base geométrica e dados do fabricante: [Freenove Hexapod Robot Kit](https://github.com/Freenove/Freenove_Hexapod_Robot_Kit), commit `1596c5ffe07a262fa7dc6d0189de6c2321270278`, e [tutorial de montagem](https://docs.freenove.com/projects/fnk0031/en/latest/fnk0031/codes/tutorial/Assembly.html). Os materiais Freenove de origem indicam **CC BY-NC-SA 3.0**; veja `LICENCA-FREENOVE.txt`. Esta disponibilização derivada preserva essa atribuição e a condição não comercial e de compartilhamento pela mesma licença. A capa editorial é ilustrativa.

Projeto e relato: [iuryeng.com.br](https://iuryeng.com.br). As carenagens cyberpunk são outro experimento e não integram este repositório.
