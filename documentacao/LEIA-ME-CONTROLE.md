# FNK0031 — controle e visualização mecânica

## Usar

Abra `FNK0031_V3_Movimento.FCStd` e execute `Iniciar_Movimento.FCMacro` em **Macro → Macros**. O painel **FNK0031 | Controle e mecanica** tem rolagem quando a janela é pequena. Mantenha a macro, o CAD, `firmware-joints.csv` e a pasta `movimento` juntos; os caminhos são relativos à macro. O CAD abre sem executar código; o painel precisa da macro.

| Modo | Movimento |
|---|---|
| Caminhar / Andar para tras | +Y / −Y |
| Lado direito / Lado esquerdo | +X / −X |
| Girar esquerda / Girar direita | Anti-horário / horário visto de cima; giro no lugar |
| Uma perna | Move somente a pata 1 |
| Subir e abaixar | Oscila a altura em ±8 mm, mantendo os alvos apoiados |
| Repouso | Seis alvos no chão; permite ajustar a postura |

Os sentidos usam o referencial inicial do modelo, não a câmera. Deslocamentos e giros executam três ciclos; os outros modos, um. **Iniciar**, **Pausar**, **Reiniciar** e a barra de fase controlam a reprodução. Trocar modo, alterar parâmetros ou arrastar a fase reposiciona imediatamente o robô; essas transições de inspeção não são manobras físicas contínuas.

**Passo**: 0–45 mm por ciclo; padrão 20. **Elevação da pata**: 0–25 mm; padrão 10. **Giro por ciclo**: 0–20°; padrão 10. **Tempo por ciclo**: 1–20 s; padrão 4. O processamento do CAD pode tornar a reprodução mais lenta.

**Ajuste de altura**: −12 a +12 mm sobre o referencial neutro de 54,25 mm. **Inclinação lateral X** e **frontal Y**: −8 a +8°, conforme a regra da mão direita. A altura indicada é a do referencial, não a folga mínima das peças. A cinemática compensa as pernas para manter os pés apoiados. **Zerar altura e inclinações** restaura esses três controles.

Combinações inalcançáveis ou fora dos limites angulares do firmware são rejeitadas antes de mudar a geometria. A última pose válida permanece visível. **Salvar pose no CAD** grava o documento atual. Não há envio de comandos ao robô físico nem gravação OBS.

## Mecânica

- **Eixos**: 18 linhas, A azul, B verde, C laranja. Nomes dos objetos incluem os ângulos.
- **Ângulos**: tabela A/B/C por perna e indicação de apoio. A aparece entre −180 e 180°; a verificação considera a equivalência de voltas completas.
- **Trajetórias**: caminhos previstos no chão para a sequência selecionada, e não rastros já executados. Grupo 1/3/5 azul, 2/4/6 magenta. Em repouso, são pontos.
- **Verificar colisões nesta pose**: pausa a animação e examina a geometria em etapas curtas por timer. Os volumes de interseção e caixas dos componentes envolvidos recebem destaque; as cores originais são preservadas.

**Vermelho**: possível colisão. **Laranja**: interface genérica servo/suporte/pé já identificada como provisória. Laranja não significa aprovação física. Mudar a pose apaga os destaques e invalida a análise. A lista informa pares e volumes; `ultima_verificacao_colisoes.json` guarda a última análise concluída.

A análise cobre 44 componentes: duas chapas do chassi e sete componentes por perna (suportes A/B, ligação, pé e servos A/B/C). Exclui pares pertencentes ao mesmo corpo rígido, salvo as 18 interfaces provisórias conhecidas. São 921 pares possíveis, filtrados por caixas envolventes antes do cálculo exato. Cabos, ferragens e eletrônica não estão incluídos. O resultado vale somente para a pose indicada, sem garantir ausência de colisão na trajetória inteira ou calcular forças de contato.

## Validação desta versão

- 48.762 posições de pernas nos nove modos: postura neutra e combinações (altura, lateral, frontal) de (5 mm, 4°, −4°) e (−5 mm, −4°, 4°). Nenhuma falha nessas trajetórias; limites do firmware respeitados.
- Erro máximo direto/inverso inferior a 8e−14 mm; desvio de apoio inferior a 1,4e−13 mm em 1e−6 ciclo. Alvos sobre/acima do chão.
- 42 poses do CAD completo: erro do terminal rígido inferior a 1,2e−13 mm.
- Parâmetro inválido rejeitado sem alterar as 19 transformações de corpo/pernas.
- Evidências em `validacao_controle_numerica.json`, `validacao_controle_geometria.json` e `validacao_controle_painel.json`.

A análise ampliada encontrou interferências antes não examinadas. Deslocamento lateral direito, fase 0,75, postura neutra: **14 possíveis colisões e 18 interfaces provisórias**, sem falhas de cálculo. Giro à esquerda, fase 0,65, altura +5 mm, lateral +4°, frontal −4°: **15 possíveis colisões e 18 interfaces provisórias**, sem falhas de cálculo. Os pares/volumes estão em `colisoes_*.json`. Incluem chapas do chassi, suportes e envelopes de servos; permanecem registrados para refinamento com as medidas reais.

## Modelo e limites

São transformações cinemáticas de 18 grupos rígidos, não juntas nativas Assembly nem simulação dinâmica. A marcha própria alterna 1/3/5 e 2/4/6, com 60% em apoio e 40% em transferência. Apoios usam âncoras fixas no chão; transferência usa interpolação horizontal de quinta ordem e elevação suave. O modo isolado mantém sua trajetória anterior. Cabos são esquemáticos.

Perfis DWG V3, comprimentos e limites vieram do repositório oficial Freenove_Hexapod_Robot_Kit, commit `1596c5ffe07a262fa7dc6d0189de6c2321270278`; arquivo FNHRBasic.cpp para cinemática/limites. A marcha não é apresentada como reprodução do algoritmo do fabricante. Licença acompanha o pacote.

Espessura de 3 mm, servos, interfaces, eletrônica e tolerâncias continuam provisórios. Não há validação física, de torque, centro de massa, equilíbrio dinâmico, cabos ou calibração. Pequenas diferenças entre ponta geométrica e alvo cinemático dependem do registro aproximado das peças. Não execute `Atualizar_Montagem.FCMacro` neste documento; ela é da montagem estática. Novas medidas exigirão revisar modelo-base e referenciais, depois repetir os testes; editar Dimensions e recomputar não atualiza todas as referências armazenadas.

O CAD atual inclui a correção anterior do chassi (Z local inferior 0, superior 30 mm). O checkpoint anterior ao painel completo está em `checkpoints/antes_painel_completo`. Arquivos antigos foram preservados; `LEIA-ME-MOVIMENTO.md` e relatórios antigos descrevem a etapa anterior. Este documento prevalece para o painel atual. O pacote novo inclui apenas os arquivos selecionados desta entrega.
