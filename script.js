  const track = document.querySelector('.carousel-track');
  const slides = Array.from(track.children);
  const prevButton = document.querySelector('.carousel-arrow.prev');
  const nextButton = document.querySelector('.carousel-arrow.next');
  
  let index = 0;

  function moveCarousel(direction) {
    if (direction === 'next') {
      index++;
      if (index >= slides.length) index = 0;
    } else {
      index--;
      if (index < 0) index = slides.length - 1;
    }
    track.style.transform = `translateX(-${index * (100 / slides.length)}%)`;
  }

  prevButton.addEventListener('click', () => moveCarousel('prev'));
  nextButton.addEventListener('click', () => moveCarousel('next'));


  setInterval(() => moveCarousel('next'), 10000);

  const citations = {
    apa: "Sahu, V. (2026). NOS-TLPlot: A Specialized Python Tool for Visualizing Newcastle–Ottawa Scale Risk-of-Bias Assessments. Journal of Open Research Software, 14(1), 7. https://doi.org/10.5334/jors.635",
    vancouver: "Sahu V. NOS-TLPlot: a specialized python tool for visualizing newcastle–ottawa scale risk-of-bias assessments. J Open Res Softw. 2026;14(1):7. doi:10.5334/jors.635",
    chicago: "Sahu, Vihaan. 2026. \"NOS-TLPlot: A Specialized Python Tool for Visualizing Newcastle–Ottawa Scale Risk-of-Bias Assessments.\" Journal of Open Research Software 14 (1): 7. https://doi.org/10.5334/jors.635.",
    harvard: "Sahu, V., 2026. ‘NOS-TLPlot: A Specialized Python Tool for Visualizing Newcastle–Ottawa Scale Risk-of-Bias Assessments’, Journal of Open Research Software, 14(1), p. 7. doi:10.5334/jors.635.",
    mla: "Sahu, Vihaan. \"NOS-TLPlot: A Specialized Python Tool for Visualizing Newcastle–Ottawa Scale Risk-of-Bias Assessments.\" Journal of Open Research Software, vol. 14, no. 1, 2026, p. 7. Crossref, https://doi.org/10.5334/jors.635.",
    ieee: "V. Sahu, \"NOS-TLPlot: A Specialized Python Tool for Visualizing Newcastle–Ottawa Scale Risk-of-Bias Assessments,\" Journal of Open Research Software, vol. 14, no. 1, p. 7, 2026."
  };

  const citationSelect = document.getElementById("citationType");
  const citationText = document.getElementById("citationText");

  citationSelect.addEventListener("change", () => {
    const selected = citationSelect.value;
    citationText.innerHTML = "<em>" + citations[selected] + "</em>";
  });

  function copyCitation() {
    navigator.clipboard.writeText(citationText.innerText).then(() => {
   
      const notification = document.createElement('div');
      notification.textContent = "Citation copied to clipboard!";
      notification.style.position = 'fixed';
      notification.style.bottom = '20px';
      notification.style.right = '20px';
      notification.style.backgroundColor = 'var(--primary-medium)';
      notification.style.color = 'white';
      notification.style.padding = '12px 20px';
      notification.style.borderRadius = '8px';
      notification.style.boxShadow = 'var(--shadow-md)';
      notification.style.zIndex = '1000';
      notification.style.fontWeight = '500';
      notification.style.opacity = '0';
      notification.style.transform = 'translateY(20px)';
      notification.style.transition = 'all 0.3s ease';
      
      document.body.appendChild(notification);
      

      setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateY(0)';
      }, 10);
      
      
      setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateY(20px)';
        setTimeout(() => {
          document.body.removeChild(notification);
        }, 300);
      }, 3000);
    });
  }
  

  function downloadCitation(format) {
    let content = "";
    let filename = "nos-tlplot_citation";
    
    if (format === 'ris') {
      content = `TY  - JOUR
T1  - NOS-TLPlot: A Specialized Python Tool for Visualizing Newcastle–Ottawa Scale Risk-of-Bias Assessments
A1  - Sahu, Vihaan
Y1  - 2026
JO  - Journal of Open Research Software
VL  - 14
IS  - 1
SP  - 7
DO  - 10.5334/jors.635
ER  - `;
      filename += ".ris";
    } else if (format === 'bibtex') {
      content = `@article{sahu2026nos,
  author = {Sahu, Vihaan},
  title = {NOS-TLPlot: A Specialized Python Tool for Visualizing Newcastle--Ottawa Scale Risk-of-Bias Assessments},
  journal = {Journal of Open Research Software},
  year = {2026},
  volume = {14},
  number = {1},
  pages = {7},
  doi = {10.5334/jors.635}
}`;
      filename += ".bib";
    }
    
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }