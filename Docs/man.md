## manual de objetos da lib

# Sumário
- [VideoStream](#videostream)
- [AudioStream](#audiostream)
- [CaptionsParser](#captionsparser)
- [VideoContent](#videocontent)
- [PlaylistContent](#playlistcontent)

### **VideoContent**

O objeto **VideoContent** representa informações gerais sobre um vídeo e possui as seguintes propriedades:

1. **title**: O título do vídeo, que geralmente é uma string representando o nome exibido na plataforma.

2. **author**: O nome do criador ou canal que publicou o vídeo.

3. **description**: A descrição do vídeo, que pode conter informações adicionais fornecidas pelo autor, como links, detalhes sobre o conteúdo ou marcações.

4. **is_private**: Um valor booleano que indica se o vídeo está configurado como privado (`True` para privado, `False` para público).

5. **thumbnails**: Uma lista ou estrutura contendo URLs das miniaturas (thumbnails) do vídeo, que podem variar em tamanho e qualidade.

6. **viewCount**: O número total de visualizações que o vídeo recebeu.

7. **Captions**: Um objeto do tipo **CaptionsParser**, utilizado para manipular legendas associadas ao vídeo. Ele permite extrair, listar ou processar legendas disponíveis.

8. **uris_stream**: Um objeto do tipo **Streams**, que permite trabalhar com streams de áudio e vídeo associados ao conteúdo. Ele facilita a obtenção de diferentes qualidades e formatos de mídia.
---

### **PlaylistContent**

O objeto **PlaylistContent** representa informações gerais sobre uma playlist e possui as seguintes propriedades:

1. **is_private**: Um valor booleano que indica se a playlist está configurada como privada (`True` para privado, `False` para pública).

2. **description**: Uma string contendo a descrição da playlist, que pode incluir informações fornecidas pelo criador, como o tema ou propósito da coleção de vídeos.

3. **playlist_name**: O nome da playlist, geralmente atribuído pelo criador e exibido como o título.

4. **image**: imagem de capa da playlist, que pode ser gerada automaticamente a partir dos vídeos contidos nela.

5. **count**: O número total de vídeos na playlist. Esse valor indica a quantidade de itens contidos na coleção.

### **CaptionsParser**

O objeto **CaptionsParser** é responsável por manipular legendas associadas a um vídeo e possui as seguintes propriedades:

1. **lang**: Uma string que representa o idioma da legenda (por exemplo, `"en"` para inglês ou `"pt"` para português).

2. **url**: O endereço (URL) onde a legenda pode ser acessada ou baixada, permitindo sua obtenção em formatos compatíveis.

3. **content**: O conteúdo completo da legenda, geralmente representado como texto formatado ou sincronizado com o tempo do vídeo.


### **VideoStream**
O objeto **VideoStream** possue as seguintes propiedades:

1. **qualityLabel**: Representa a qualidade do vídeo. É um valor descritivo indicando a qualidade do stream.

2. **url**: O endereço (URL) onde o stream de vídeo pode ser acessado, permitindo que o vídeo seja carregado ou transmitido.

3. **quality**: Um identificador numérico ou codificado que refere-se à qualidade do stream.

4. **width**: A largura do vídeo em pixels. Representa a dimensão horizontal da resolução do vídeo.

5. **height**: A altura do vídeo em pixels. Representa a dimensão vertical da resolução do vídeo.

6. **approxDurationMs**: A duração aproximada do vídeo em milissegundos. Pode ser útil para calcular o tempo total de exibição ou controle de progresso do vídeo.

7. **audioChannels**: Número de canais de áudio presentes no stream. Pode ser 1 (mono), 2 (estéreo).

8. **averageBitrate**: A taxa média de bits do stream de vídeo, expressa em bits por segundo (bps). Isso reflete a quantidade de dados usados para transmitir o vídeo e o áudio.

9. **bitrate**: A taxa de bits do stream, podendo se referir especificamente ao bitrate do vídeo ou do áudio, em contraste com o `averageBitrate` que é uma média ao longo do tempo.

10. **fps**: Frames por segundo, indicando a taxa de quadros que o vídeo possui. Valores típicos são 24fps, 30fps ou 60fps, com vídeos de maior FPS proporcionando movimentos mais suaves.

11. **projectionType**: Tipo de projeção do vídeo

12. **indexRange**: Intervalo de índices de bytes no stream que representa a parte do arquivo a ser carregada ou transmitida, geralmente usado em técnicas de transmissão progressiva ou streaming adaptativo.

13. **itag**: Um identificador único do formato ou qualidade específica do stream de vídeo. O `itag` é usado para referir-se a uma combinação particular de áudio e vídeo no contexto de plataformas como o YouTube.

14. **mimeType**: O tipo MIME (Multipurpose Internet Mail Extensions) do stream, indicando o formato de mídia (como "video/mp4", "audio/webm", etc.).

15. **audioSampleRate**: A taxa de amostragem do áudio, medida em Hertz (Hz).

16. **lastModified**: A data e hora da última modificação do stream ou do arquivo associado ao vídeo. Pode ser importante para controle de versões ou caching.

17. **contentLength**: O tamanho total do arquivo do stream em bytes. Essa propriedade pode ser usada para calcular o tempo de download ou a quantidade de dados que serão transmitidos.

### **AudioStream**

O objeto **AudioStream** possue as seguintes propiedades:

1. **url**: O endereço (URL) onde o stream de áudio pode ser acessado. Esse URL permite o carregamento ou a transmissão do áudio.

2. **quality**: Identificador numérico ou codificado que descreve a qualidade do stream de áudio

3. **audioChannels**: Número de canais de áudio presentes no stream. Pode ser 1 (mono), 2 (estéreo).

4. **approxDurationMs**: A duração aproximada do stream de áudio em milissegundos, útil para controlar o tempo de reprodução ou progresso.

5. **averageBitrate**: A taxa média de bits do stream de áudio, expressa em bits por segundo (bps). Reflete a quantidade de dados usada para transmitir o áudio.

6. **bitrate**: A taxa de bits do stream, podendo se referir ao bitrate específico do áudio em um determinado momento ou média ao longo do tempo.

7. **projectionType**: Indica o tipo de projeção, mas no caso de áudio, geralmente é "mono" ou "stereo", dependendo da configuração do stream.

8. **indexRange**: Intervalo de índices de bytes no stream de áudio, indicando a parte do arquivo que será transmitida ou carregada. Usado em streaming adaptativo.

9. **itag**: Identificador único que refere-se ao formato ou qualidade específica do stream de áudio.

10. **mimeType**: O tipo MIME (Multipurpose Internet Mail Extensions) do stream de áudio, que indica o formato de mídia (como "audio/mp4", "audio/webm", etc.).

11. **audioSampleRate**: A taxa de amostragem do áudio, medida em Hertz (Hz).

12. **lastModified**: Data e hora da última modificação do stream ou do arquivo associado ao áudio. Importante para controle de versões e cache.

13. **contentLength**: O tamanho total do arquivo de áudio em bytes. Usado para calcular o tempo de download ou a quantidade de dados que será transmitida.

14. **loudnessDb**: A medida de intensidade de volume do áudio, expressa em decibéis (dB). Essa propriedade pode ser usada para normalizar o volume do áudio durante a reprodução.

15. **audioQuality**: Indicador da qualidade do áudio.

16. **highReplication**: Um indicador se o stream de áudio possui replicação de alta qualidade, com cópias redundantes ou melhor distribuição, assegurando maior disponibilidade e qualidade.
ou seja cada vez que você obtiver um Objeto do tipo de AudioStream ele possue essas propieades

---