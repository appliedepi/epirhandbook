# The Epidemiologist R Handbook 

# About this handbook
**The Epi R Handbook is a R reference manual for applied epidemiology and public health.**  

***Go to www.epiRhandbook.com to see the latest version of the online handbook.***

![Project logo](https://github.com/appliedepi/epiRhandbook_eng/blob/master/images/Epi%20R%20Handbook%20Banner%20Beige%201500x500.png)

**This book strives to:**  

* Serve as a quick epi R code reference manual  
* Provide task-centered examples addressing common epidemiological problems  
* Assist epidemiologists transitioning to R  
* Be accessible in settings with low internet-connectivity via an **offline version**
  

<img src="https://github.com/appliedepi/epiRhandbook_eng/blob/master/images/epiRhandbook_HexSticker_500x500.png" width="200" height="200">

<span style="color: black;">**Written by epis, for epis**</span>
We are applied epis from around the world, writing in our spare time to offer this resource to the community. Your encouragement and feedback is most welcome:  

* Structured **[feedback form](https://forms.gle/A5SnRVws7tPD15Js9)**  
* Email **epiRhandbook@gmail.com** or tweet **[\@epiRhandbook](https://twitter.com/epirhandbook)**  
* Submit issues to our **[Github repository](https://github.com/epirhandbook/Epi_R_handbook)**  


## How to use this handbook  


* Browse the pages in the Table of Contents, or use the search box
* Click the "copy" icons to copy code  
* You can follow-along with [the example data][Download handbook and data]  
* See the "Resources" section of each page for further material  

**Offline version**  

See instructions in the [Download handbook and data] page.  

**Languages**  

We want to translate this into languages other than English. If you can help, please contact us.  




<!-- ======================================================= -->
## Acknowledgements   

This handbook is produced by a collaboration of epidemiologists from around the world drawing upon experience with organizations including local, state, provincial, and national health agencies, the World Health Organization (WHO), Médecins Sans Frontières / Doctors without Borders (MSF), hospital systems, and academic institutions.

This handbook is **not** an approved product of any specific organization. Although we strive for accuracy, we provide no guarantee of the content in this book.  



### Contributors  

**Editor:** [Neale Batra](https://www.linkedin.com/in/neale-batra/) 

**Project core team:** [Neale Batra](https://www.linkedin.com/in/neale-batra/), [Alex Spina](https://github.com/aspina7), [Amrish Baidjoe](https://twitter.com/Ammer_B), Pat Keating, [Henry Laurenson-Schafer](https://github.com/henryls1), [Finlay Campbell](https://github.com/finlaycampbell)  

**Authors**: [Neale Batra](https://www.linkedin.com/in/neale-batra/), [Alex Spina](https://github.com/aspina7), [Paula Blomquist](https://www.linkedin.com/in/paula-bianca-blomquist-53188186/), [Finlay Campbell](https://github.com/finlaycampbell), [Henry Laurenson-Schafer](https://github.com/henryls1), [Isaac Florence](www.Twitter.com/isaacatflorence), [Natalie Fischer](www.linkedin.com/in/nataliefischer211), [Aminata Ndiaye](https://twitter.com/aminata_fadl), [Liza Coyer]( https://www.linkedin.com/in/liza-coyer-86022040/), [Jonathan Polonsky](https://twitter.com/jonny_polonsky), [Yurie Izawa](https://ch.linkedin.com/in/yurie-izawa-a1590319), [Chris Bailey](https://twitter.com/cbailey_58?lang=en), [Daniel Molling](https://www.linkedin.com/in/daniel-molling-4005716a/), [Isha Berry](https://twitter.com/ishaberry2), [Emma Buajitti](https://twitter.com/buajitti), [Mathilde Mousset](https://mathildemousset.wordpress.com/research/), [Sara Hollis](https://www.linkedin.com/in/saramhollis/), Wen Lin  

**Reviewers**: Pat Keating, Annick Lenglet, Margot Charette, Daniely Xavier, Esther Kukielka, Michelle Sloan, Aybüke Koyuncu, Rachel Burke, Kate Kelsey, [Berhe Etsay](https://www.linkedin.com/in/berhe-etsay-5752b1154/), John Rossow, Mackenzie Zendt, James Wright, Laura Haskins, [Flavio Finger](ffinger.github.io), Tim Taylor, [Jae Hyoung Tim Lee](https://www.linkedin.com/in/jaehyoungtlee/), [Brianna Bradley](https://www.linkedin.com/in/brianna-bradley-bb8658155), [Wayne Enanoria](https://www.linkedin.com/in/wenanoria), Manual Albela Miranda, [Molly Mantus](https://www.linkedin.com/in/molly-mantus-174550150/), Pattama Ulrich, Joseph Timothy, Adam Vaughan, Olivia Varsaneux, Lionel Monteiro, Joao Muianga  

**Illustrations**: Calder Fong  


<!-- **Editor-in-Chief:** Neale Batra  -->

<!-- **Project core team:** Neale Batra, Alex Spina, Amrish Baidjoe, Pat Keating, Henry Laurenson-Schafer, Finlay Campbell   -->

<!-- **Authors**: Neale Batra, Alex Spina, Paula Blomquist, Finlay Campbell, Henry Laurenson-Schafer, [Isaac Florence](www.Twitter.com/isaacatflorence), Natalie Fischer, Aminata Ndiaye, Liza Coyer, Jonathan Polonsky, Yurie Izawa, Chris Bailey, Daniel Molling, Isha Berry, Emma Buajitti, Mathilde Mousset, Sara Hollis, Wen Lin   -->

<!-- **Reviewers**: Pat Keating, Mathilde Mousset, Annick Lenglet, Margot Charette, Isha Berry, Paula Blomquist, Natalie Fischer, Daniely Xavier, Esther Kukielka, Michelle Sloan, Aybüke Koyuncu, Rachel Burke, Daniel Molling, Kate Kelsey, Berhe Etsay, John Rossow, Mackenzie Zendt, James Wright, Wayne Enanoria, Laura Haskins, Flavio Finger, Tim Taylor, Jae Hyoung Tim Lee, Brianna Bradley, Manual Albela Miranda, Molly Mantus, Priscilla Spencer, Pattama Ulrich, Joseph Timothy, Adam Vaughan, Olivia Varsaneux, Lionel Monteiro, Joao Muianga   -->


### Funding and support   


The handbook received supportive funding via a COVID-19 emergency capacity-building grant from [TEPHINET](https://www.tephinet.org/), the global network of Field Epidemiology Training Programs (FETPs).  

Administrative support was provided by the EPIET Alumni Network ([EAN](https://epietalumni.net/)), with special thanks to Annika Wendland. EPIET is the European Programme for Intervention Epidemiology Training.  

Special thanks to Médecins Sans Frontières (MSF) Operational Centre Amsterdam (OCA) for their support during the development of this handbook.  


*This publication was supported by Cooperative Agreement number NU2GGH001873, funded by the Centers for Disease Control and Prevention through TEPHINET, a program of The Task Force for Global Health. Its contents are solely the responsibility of the authors and do not necessarily represent the official views of the Centers for Disease Control and Prevention, the Department of Health and Human Services, The Task Force for Global Health, Inc. or TEPHINET.*

### Inspiration   

The multitude of tutorials and vignettes that provided knowledge for development of handbook content are credited within their respective pages.  

More generally, the following sources provided inspiration for this handbook:  
[The "R4Epis" project](https://r4epis.netlify.app/) (a collaboration between MSF and RECON)  
[R Epidemics Consortium (RECON)](https://www.repidemicsconsortium.org/)  
[R for Data Science book (R4DS)](https://r4ds.had.co.nz/)  
[bookdown: Authoring Books and Technical Documents with R Markdown](https://bookdown.org/yihui/bookdown/)  
[Netlify](https://www.netlify.com) hosts this website  


<!-- ### Image credits {-}   -->

<!-- Images in logo from US CDC Public Health Image Library) include [2013 Yemen looking for mosquito breeding sites](https://phil.cdc.gov/Details.aspx?pid=19623), [Ebola virus](https://phil.cdc.gov/Details.aspx?pid=23186), and [Survey in Rajasthan](https://phil.cdc.gov/Details.aspx?pid=19838).   -->


## Terms of Use and License   

<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License</a>.


Academic courses and epidemiologist training programs are welcome to use this handbook with their students. If you have questions about your intended use, email **epirhandbook@gmail.com**.  


## Citation  

Batra, Neale et al. (2021), The Epidemiologist R Handbook. <a rel="license" href="https://zenodo.org/badge/231610102.svg"><img alt="DOI" style="border-width:0" src="https://zenodo.org/badge/231610102.svg" /></a><br />



## Contribution

If you would like to make a content contribution, please contact with us first via Github issues or by email. We are implementing a schedule for updates and are creating a contributor guide.  

Please note that the epiRhandbook project is released with a [Contributor Code of Conduct](https://contributor-covenant.org/version/2/0/CODE_OF_CONDUCT.html). By contributing to this project, you agree to abide by its terms.

