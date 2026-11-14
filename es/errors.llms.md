# 47  Errores comunes

Esta página incluye una lista actualizada de los errores más comunes y sugiere soluciones para solucionarlos.

## 47.1 Interpretación de los mensajes de error

Los mensajes de error de R pueden ser crípticos a veces, así que Google es su amigo. Busque el mensaje de error con “R” y busque publicaciones recientes en [StackExchange.com](https://StackExchange.com), [stackoverflow.com](https://stackoverflow.com), [community.rstudio.com](https://community.rstudio.com), twitter (#rstats) y otros foros utilizados por los programadores para archivar preguntas y respuestas. Intente encontrar publicaciones recientes que hayan resuelto problemas similares.

Si después de mucho buscar no encuentra una respuesta a su problema, considere la posibilidad de crear un ejemplo *reproducible* (“reprex”) y publicar usted mismo la pregunta. Consulte la página sobre [Cómo obtener ayuda](help.llms.md) para obtener consejos sobre cómo crear y publicar un ejemplo reproducible en los foros.

## 47.2 Errores comunes

A continuación, enumeramos algunos errores comunes y posibles explicaciones/soluciones. Algunos de ellos se han tomado prestados de Noam Ross, que analizó los mensajes más comunes del foro en Stack Overflow sobre los mensajes de error de R (véase el análisis [aquí](https://github.com/noamross/zero-dependency-problems/blob/master/misc/stack-overflow-common-r-errors.md))

### Errores tipográficos

    Error: unexpected symbol in:
    "  geom_histogram(stat = "identity")+
      tidyquant::geom_ma(n=7, size = 2, color = "red" lty"

Si aparece “unexpected symbol” (símbolo inesperado), compruebe si faltan comas

### Errores del paquete

    could not find function "x"...

Esto probablemente significa que ha escrito mal el nombre de la función, o que ha olvidado instalar o cargar un paquete.

    Error in select(data, var) : unused argument (var)

Cree que está usando `dplyr::select()` pero la función `select()` ha sido enmascarada por `MASS::select()` - especifique `dplyr::` o reordene la carga de su paquete para que dplyr esté después de todos los demás.

Otros errores de enmascaramiento comunes provienen de: `plyr::summarise()` y `stats::filter()`. Considere la posibilidad de utilizar el [paquete **conflicted**](https://www.tidyverse.org/blog/2018/06/conflicted/).

    Error in install.packages : ERROR: failed to lock directory ‘C:\Users\Name\Documents\R\win-library\4.0’ for modifying
    Try removing ‘C:\Users\Name\Documents\R\win-library\4.0/00LOCK’

Si recibe un error que dice que necesita eliminar un archivo “00LOCK”, vaya a su biblioteca “R” en el directorio de su ordenador (por ejemplo, R/win-library/) y busque una carpeta llamada “00LOCK”. Elimínela manualmente e intente instalar el paquete de nuevo. Es probable que un proceso de instalación anterior se haya interrumpido, provocando este error.

### Errores en los objetos

    No such file or directory:

Si aparece un error como este al exportar o importar, compruebe la ortografía del archivo y de la ruta de acceso, y si la ruta contiene barras inclinadas, asegúrese de que son hacia delante `/` y no hacia atrás `\`. Asegúrese también de que ha utilizado la extensión de archivo correcta (por ejemplo, .csv, .xlsx).

    object 'x' not found 

Esto significa que el objeto al que se hace referencia no existe. ¿Quizá el código anterior no se ha ejecutado correctamente?

    Error in 'x': subscript out of bounds

Esto significa que ha intentado acceder a algo (un elemento de un vector o una lista) que no estaba allí.

### Errores de sintaxis de las funciones

    # se ejecutó recode sin reiniciar la variable x en mutate(x = recode(x, OLD = NEW)
    Error: Problem with `mutate()` input `hospital`.
    x argument ".x" is missing, with no default
    i Input `hospital` is `recode(...)`.

Este error de arriba (`argument .x is missing, with no default`) es común en `mutate()` si está suministrando una función como `recode()` o `replace_na()` donde se espera que proporcione el nombre de la columna como primer argumento. Esto es fácil de olvidar.

### Errores lógicos

    Error in if

Esto probablemente significa que se aplicó una sentencia `if` a algo que no era TRUE o FALSE.

### Errores de los factores

    #Se intentó añadir un valor ("Missing") a un factor (con replace_na operando en un factor)
    Problem with `mutate()` input `age_cat`.
    i invalid factor level, NA generated
    i Input `age_cat` is `replace_na(age_cat, "Missing")`.invalid factor level, NA generated

Si aparece este error sobre niveles de factor no válidos, es probable que tenga una columna de tipo Factor (que contiene niveles predefinidos) y haya intentado añadirle un nuevo valor. Conviértala al tipo Carácter antes de añadir un nuevo valor.

### Errores de trazado

`Error: Insufficient values in manual scale. 3 needed but only 2 provided.` ggplot() scale_fill_manual() values = c(“orange”, “purple”) … insuficiente para el número de niveles del factor … considere si NA es ahora un nivel del factor…

    Can't add x object

Probablemente tiene un `+` extra al final de un comando ggplot que necesita eliminar.

### Errores de R Markdown

Si el mensaje de error contiene algo como `Error in options[[sprintf("fig.%s", i)]]`, compruebe que sus opciones knitr en la parte superior de cada bloque de código utilizan correctamente `out.width =` o `out.height =`y *no* `fig.width=` y `fig.height=`.

### Miscelánea

Compruebe si ha reordenado los verbos **dplyr** y no ha reemplazado un pipe en el medio, o no ha eliminado un pipe del final después de reordenar.

## 47.3 Recursos

Esta es otra entrada del blog que enumera los [errores comunes de programación en R a los que se enfrentan los principiantes](https://www.r-bloggers.com/2016/06/common-r-programming-errors-faced-by-beginners/)
