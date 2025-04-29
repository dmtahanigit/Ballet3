/**
 * World Ballets - Mock Data
 * 
 * This module provides mock data for the World Ballets website.
 * It's used as a fallback when the API is unavailable.
 */

const MockData = (() => {
    // Mock data for demonstration purposes
    const data = {
        companies: {
            abt: {
                name: "American Ballet Theatre",
                shortName: "ABT",
                logo: "https://placehold.co/150x150?text=ABT+Logo",
                description: "Founded in 1940, American Ballet Theatre is recognized as one of the world's leading classical ballet companies. Based in New York City, ABT annually tours the United States and around the world.",
                website: "https://www.abt.org"
            },
            "paris-opera-ballet": {
                name: "Paris Opera Ballet",
                shortName: "POB",
                logo: "https://placehold.co/150x150?text=POB+Logo",
                description: "The Paris Opera Ballet is the oldest national ballet company in the world, founded in 1669. It is the ballet company of the Paris Opera and is one of the most prestigious ballet companies in the world.",
                website: "https://www.operadeparis.fr/en/artists/ballet"
            },
            bolshoi: {
                name: "Bolshoi Ballet",
                shortName: "BOLSHOI",
                logo: "https://placehold.co/150x150?text=BOLSHOI+Logo",
                description: "The Bolshoi Ballet is an internationally renowned classical ballet company, based at the Bolshoi Theatre in Moscow, Russia. Founded in 1776, the Bolshoi is among the world's oldest and most prestigious ballet companies.",
                website: "https://www.bolshoi.ru/en/"
            },
            royal: {
                name: "The Royal Ballet",
                shortName: "ROYAL",
                logo: "https://placehold.co/150x150?text=ROYAL+Logo",
                description: "The Royal Ballet is an internationally renowned classical ballet company, based at the Royal Opera House in Covent Garden, London, England. Founded in 1931, it is one of the world's greatest ballet companies.",
                website: "https://www.roh.org.uk/about/the-royal-ballet"
            },
            rb: {
                name: "The Royal Ballet",
                shortName: "RB",
                logo: "https://placehold.co/150x150?text=RB+Logo",
                description: "The Royal Ballet is one of the world's greatest ballet companies. Based at the Royal Opera House in London's Covent Garden, it brings together today's most dynamic and versatile dancers with a world-class orchestra and leading choreographers, composers, conductors, directors and creative teams to share awe-inspiring theatrical experiences with diverse audiences worldwide.",
                website: "https://www.roh.org.uk/about/the-royal-ballet"
            },
            stuttgart: {
                name: "Stuttgart Ballet",
                shortName: "STUTTGART",
                logo: "https://placehold.co/150x150?text=STUTTGART+Logo",
                description: "The Stuttgart Ballet is a leading German ballet company based in Stuttgart, Germany. Known for its innovative choreography and technical excellence, it has been a major influence in the ballet world since the 1960s.",
                website: "https://www.stuttgart-ballet.de/en/"
            },
            boston: {
                name: "Boston Ballet",
                shortName: "BOSTON",
                logo: "https://placehold.co/150x150?text=BOSTON+Logo",
                description: "Founded in 1963, Boston Ballet is one of the leading dance companies in North America. The company maintains an internationally acclaimed repertoire and the largest ballet school in North America.",
                website: "https://www.bostonballet.org"
            },
            nbc: {
                name: "National Ballet of Canada",
                shortName: "NBC",
                logo: "https://placehold.co/150x150?text=NBC+Logo",
                description: "Founded in 1951, the National Ballet of Canada is one of the premier dance companies in North America. Based in Toronto, the company performs a traditional and contemporary repertoire of the highest caliber.",
                website: "https://national.ballet.ca"
            }
        },
        performances: {
            "paris-opera-ballet": [
                {
                    id: "pob-1",
                    title: "MAYERLING",
                    company: "paris-opera-ballet",
                    startDate: "2024-10-29",
                    endDate: "2024-11-16",
                    description: "A ballet at Opéra Palais Garnier in Paris from October 29th to November 16th, 2024. This classic ballet combines love, royalty, and politics into one completely enrapturing performance that is indisputably the best-loved work of acclaimed choreographer Kenneth MacMillan.",
                    image: "https://placehold.co/800x400?text=POB+Performance",
                    videoUrl: "",
                    venue: "Opéra Palais Garnier",
                    isCurrent: false,
                    isNext: true
                },
                {
                    id: "pob-2",
                    title: "ONEGIN",
                    company: "paris-opera-ballet",
                    startDate: "2025-02-08",
                    endDate: "2025-03-04",
                    description: "A ballet at Opéra Palais Garnier in Paris from February 8th to March 4th, 2025. In a glorious performance which combines two of Russia's most famous artists, Tchaikovsky's music and Pushkin's prose, this classic ballet is a gorgeous spectacle of love, loss, and drama.",
                    image: "https://placehold.co/800x400?text=POB+Performance",
                    videoUrl: "",
                    venue: "Opéra Palais Garnier",
                    isCurrent: false,
                    isNext: false
                },
                {
                    id: "pob-3",
                    title: "THE SLEEPING BEAUTY",
                    company: "paris-opera-ballet",
                    startDate: "2025-03-08",
                    endDate: "2025-07-10",
                    description: "A ballet at Opéra Bastille in Paris from March 8th to July 10th, 2025. A tale as old as time… This stunning classic ballet is an entirely new and magical way to experience the love story and dreamy slumber of the classic fairy tale heroine Aurora. Filled with fairies, tulle, and of course, a Prince Charming, this Charles Perrault ballet is sure to delight all audiences!",
                    image: "https://placehold.co/800x400?text=POB+Performance",
                    videoUrl: "",
                    venue: "Opéra Bastille",
                    isCurrent: false,
                    isNext: false
                },
                {
                    id: "pob-4",
                    title: "SYLVIA",
                    company: "paris-opera-ballet",
                    startDate: "2024-05-08",
                    endDate: "2024-06-04",
                    description: "A ballet at Opéra Palais Garnier in Paris from May 8th to June 4th, 2024. In a joyous homecoming, the very first ballet created for the Opéra de Paris in 1876 by Louis Mérante takes the stage once again! Full of woodland wonder, love, jealousy and gorgeous dancing, this will be a ballet to remember.",
                    image: "https://placehold.co/800x400?text=POB+Performance",
                    videoUrl: "",
                    venue: "Opéra Palais Garnier",
                    isCurrent: false,
                    isNext: false
                }
            ],
            rb: [
                {
                    id: "rb-1",
                    title: "Balanchine: Three Signature Works",
                    company: "rb",
                    startDate: "2025-03-28",
                    endDate: "2025-04-08",
                    description: "Sensuous and shimmering beauty in three works by the man who defined American ballet. With its extreme speed, dynamism and athleticism, Balanchine's choreography pushed the boundaries of the art form. This program features three of Balanchine's most celebrated works: 'Apollo', 'Agon', and 'Symphony in C', showcasing the Royal Ballet dancers' technical brilliance and artistic versatility.",
                    image: "https://placehold.co/800x400?text=Balanchine+Three+Signature+Works",
                    videoUrl: "https://www.youtube.com/embed/XFzSh-XVhBw",
                    isCurrent: true,
                    isNext: false
                },
                {
                    id: "rb-2",
                    title: "Romeo and Juliet",
                    company: "rb",
                    startDate: "2025-04-15",
                    endDate: "2025-05-02",
                    description: "Kenneth MacMillan's passionate choreography for Romeo and Juliet shows The Royal Ballet at its dramatic finest. Set to Prokofiev's iconic score, this production has been a cornerstone of the Company's repertory since its creation in 1965. The doomed lovers attempt to find their way through the color and action of Renaissance Verona, where a busy market all too quickly bursts into sword fighting and a family feud leads to tragedy for both the Montagues and the Capulets.",
                    image: "https://placehold.co/800x400?text=Romeo+and+Juliet",
                    videoUrl: "https://www.youtube.com/embed/AhB9UoQXr0U",
                    isCurrent: false,
                    isNext: true
                },
                {
                    id: "rb-3",
                    title: "Swan Lake",
                    company: "rb",
                    startDate: "2025-05-10",
                    endDate: "2025-05-28",
                    description: "The Royal Ballet's sumptuous production of Swan Lake returns to the Royal Opera House stage. Prince Siegfried chances upon a flock of swans while out hunting. When one of the swans turns into a beautiful woman, Odette, he is enraptured. But she is under a spell that holds her captive, allowing her to regain her human form only at night. Liam Scarlett's glorious production, with its spectacular designs by John Macfarlane, is a testament to the Company's heritage and a must-see for ballet lovers.",
                    image: "https://placehold.co/800x400?text=Swan+Lake",
                    videoUrl: "https://www.youtube.com/embed/9rJoB7y6Ncs",
                    isCurrent: false,
                    isNext: false
                },
                {
                    id: "rb-4",
                    title: "The Sleeping Beauty",
                    company: "rb",
                    startDate: "2025-06-05",
                    endDate: "2025-06-20",
                    description: "The Sleeping Beauty holds a very special place in The Royal Ballet's heart and history. It was the first performance given by the Company when the Royal Opera House reopened at Covent Garden in 1946 after World War II. In 2006, this original staging was revived and has been delighting audiences ever since. The masterful 19th-century choreography of Marius Petipa is combined with sections created for The Royal Ballet by Frederick Ashton, Anthony Dowell and Christopher Wheeldon.",
                    image: "https://placehold.co/800x400?text=The+Sleeping+Beauty",
                    videoUrl: "https://www.youtube.com/embed/1-94SzKX1Wo",
                    isCurrent: false,
                    isNext: false
                },
                {
                    id: "rb-5",
                    title: "Woolf Works",
                    company: "rb",
                    startDate: "2025-07-08",
                    endDate: "2025-07-19",
                    description: "Wayne McGregor's ballet triptych Woolf Works, inspired by the writings of Virginia Woolf, returns to the Royal Opera House. Named \"a compellingly moving experience\" by The Independent, Woolf Works met with outstanding critical acclaim on its premiere in 2015, and went on to win McGregor the Critics' Circle Award for Best Classical Choreography and the Olivier Award for Best New Dance Production. The ballet is inspired by three of Woolf's novels: Mrs Dalloway, Orlando, and The Waves, and features music by Max Richter.",
                    image: "https://placehold.co/800x400?text=Woolf+Works",
                    videoUrl: "https://www.youtube.com/embed/QwCmTjJZPo8",
                    isCurrent: false,
                    isNext: false
                },
                {
                    id: "rb-6",
                    title: "The Nutcracker",
                    company: "rb",
                    startDate: "2025-12-05",
                    endDate: "2025-12-30",
                    description: "The Royal Ballet's glorious production of The Nutcracker, created by Peter Wright in 1984, is the production par excellence of an all-time ballet favorite. On Christmas Eve, Clara receives an enchanted Nutcracker as a gift. Together they defeat the Mouse King and journey through the glistening Land of Snow to the Kingdom of Sweets, where the Sugar Plum Fairy and her Prince greet them with a celebration of dances from around the world. Tchaikovsky's score contains some of ballet's most memorable music, from the delicate Dance of the Sugar Plum Fairy to the iconic Waltz of the Flowers.",
                    image: "https://placehold.co/800x400?text=The+Nutcracker",
                    videoUrl: "https://www.youtube.com/embed/so5HKPJvCBM",
                    isCurrent: false,
                    isNext: false
                }
            ],
            nbc: [
                {
                    id: "nbc-1",
                    title: "Romeo and Juliet",
                    company: "nbc",
                    startDate: "2025-03-20",
                    endDate: "2025-04-10",
                    description: "Alexei Ratmansky's passionate reimagining of Shakespeare's tragic love story set to Prokofiev's powerful score. This innovative production brings fresh perspective to the classic tale of star-crossed lovers, featuring breathtaking choreography that highlights the technical brilliance of the company's dancers. Ratmansky's interpretation balances dramatic storytelling with pure classical dance, creating a Romeo and Juliet for today's audiences while honoring the ballet's rich tradition.",
                    image: "https://placehold.co/800x400?text=Romeo+and+Juliet",
                    videoUrl: "https://www.youtube.com/embed/4fHw4GeW3EU",
                    isCurrent: true,
                    isNext: false
                },
                {
                    id: "nbc-2",
                    title: "Spring Mixed Program",
                    company: "nbc",
                    startDate: "2025-05-05",
                    endDate: "2025-05-15",
                    description: "A vibrant collection of contemporary works featuring Crystal Pite's 'Angels' Atlas' and Balanchine's 'Serenade'. This dynamic program showcases the versatility of the company with three distinct pieces that span the range of ballet today. Crystal Pite's 'Angels' Atlas' explores themes of mortality and navigation with her signature blend of ballet and contemporary movement. Balanchine's 'Serenade', set to Tchaikovsky's Serenade for Strings, was the choreographer's first original ballet created in America and remains a timeless masterpiece of neoclassical beauty.",
                    image: "https://placehold.co/800x400?text=Spring+Mixed+Program",
                    videoUrl: "https://www.youtube.com/embed/Urz4v1JVXZQ",
                    isCurrent: false,
                    isNext: true
                },
                {
                    id: "nbc-3",
                    title: "Giselle",
                    company: "nbc",
                    startDate: "2025-06-10",
                    endDate: "2025-06-20",
                    description: "The romantic classic of love, betrayal, and forgiveness with ethereal choreography and Adolphe Adam's memorable score. One of the oldest continually performed ballets, Giselle tells the story of a peasant girl who dies of a broken heart after discovering her lover is betrothed to another. The Wilis, a group of supernatural women who dance men to death, summon Giselle from her grave. They target her lover for death, but Giselle's love frees him from their grasp. The National Ballet of Canada's production features exquisite costumes and sets that transport audiences to a world of romantic beauty and supernatural wonder.",
                    image: "https://placehold.co/800x400?text=Giselle",
                    videoUrl: "https://www.youtube.com/embed/eSx_kqe6ox0",
                    isCurrent: false,
                    isNext: false
                },
                {
                    id: "nbc-4",
                    title: "The Nutcracker",
                    company: "nbc",
                    startDate: "2025-12-10",
                    endDate: "2025-12-31",
                    description: "The beloved holiday classic returns with Tchaikovsky's magical score and James Kudelka's enchanting choreography. This distinctly Canadian production follows Misha and Marie on a magical Christmas Eve adventure. After receiving a nutcracker from their Uncle Nikolai, they embark on a journey through the glittering Kingdom of Snow and the delicious Land of Sweets. Featuring over 200 performers and dazzling sets and costumes by Santo Loquasto, this Nutcracker has been a cherished holiday tradition since its premiere in 1995.",
                    image: "https://placehold.co/800x400?text=The+Nutcracker",
                    videoUrl: "https://www.youtube.com/embed/YR5USHu6D6U",
                    isCurrent: false,
                    isNext: false
                },
                {
                    id: "nbc-5",
                    title: "Swan Lake",
                    company: "nbc",
                    startDate: "2026-03-05",
                    endDate: "2026-03-20",
                    description: "The timeless tale of love and deception featuring Tchaikovsky's iconic score and Karen Kain's breathtaking choreography. This production honors the classical legacy of Swan Lake while incorporating fresh perspectives that highlight the technical and artistic excellence of the company. The story follows Prince Siegfried as he falls in love with Odette, a princess transformed into a swan by the evil sorcerer Von Rothbart. The ballet's famous white acts, featuring the corps de ballet as a flock of swans, showcase some of the most beautiful and challenging choreography in the classical repertoire.",
                    image: "https://placehold.co/800x400?text=Swan+Lake",
                    videoUrl: "https://www.youtube.com/embed/9rJoB7y6Ncs",
                    isCurrent: false,
                    isNext: false
                }
            ],
            abt: [
                {
                    id: "abt-1",
                    title: "Swan Lake",
                    company: "abt",
                    startDate: "2025-03-25",
                    endDate: "2025-04-05",
                    description: "American Ballet Theatre's sumptuous production of Swan Lake, choreographed by Kevin McKenzie after Marius Petipa and Lev Ivanov, features Tchaikovsky's iconic score and exquisite costumes by Zack Brown. This beloved classic tells the story of Odette, a princess turned into a swan by an evil sorcerer's curse. Prince Siegfried's love for her breaks the spell, but the sorcerer's deception leads to tragedy. ABT's production showcases the company's extraordinary dancers in one of ballet's most technically and emotionally demanding works.",
                    image: "https://placehold.co/800x400?text=ABT+Swan+Lake",
                    videoUrl: "https://www.youtube.com/embed/9rJoB7y6Ncs",
                    isCurrent: true,
                    isNext: false
                },
                {
                    id: "abt-2",
                    title: "Don Quixote",
                    company: "abt",
                    startDate: "2025-05-15",
                    endDate: "2025-05-25",
                    description: "ABT's vibrant production of Don Quixote, staged by Kevin McKenzie and Susan Jones, brings Ludwig Minkus's score and the colorful world of Cervantes's novel to life. This comedic ballet follows the adventures of the eccentric knight Don Quixote and his faithful squire Sancho Panza as they encounter the spirited Kitri and her lover Basilio. With its Spanish-inspired choreography, dazzling technique, and charismatic characters, Don Quixote is a joyous celebration of love, adventure, and the rich traditions of classical ballet.",
                    image: "https://placehold.co/800x400?text=ABT+Don+Quixote",
                    videoUrl: "https://www.youtube.com/embed/IGzJiRrIBGk",
                    isCurrent: false,
                    isNext: true
                },
                {
                    id: "abt-3",
                    title: "Romeo and Juliet",
                    company: "abt",
                    startDate: "2025-06-20",
                    endDate: "2025-06-30",
                    description: "Kenneth MacMillan's masterful interpretation of Shakespeare's enduring romantic tragedy has become one of ABT's signature productions. Set to Prokofiev's magnificent score, this Romeo and Juliet features breathtaking choreography, sword fights, and passionate pas de deux that bring the star-crossed lovers' story to life. With Renaissance-inspired designs by Nicholas Georgiadis and emotional depth that resonates with audiences of all ages, this production showcases the dramatic and technical prowess of ABT's dancers.",
                    image: "https://placehold.co/800x400?text=ABT+Romeo+and+Juliet",
                    videoUrl: "https://www.youtube.com/embed/4fHw4GeW3EU",
                    isCurrent: false,
                    isNext: false
                },
                {
                    id: "abt-4",
                    title: "Giselle",
                    company: "abt",
                    startDate: "2025-10-15",
                    endDate: "2025-10-25",
                    description: "ABT's production of Giselle, staged by Kevin McKenzie after Jean Coralli, Jules Perrot, and Marius Petipa, epitomizes the Romantic ballet tradition. This haunting tale of love, betrayal, and forgiveness follows a peasant girl who dies of a broken heart after discovering her beloved is betrothed to another. In the moonlit world of the Wilis—vengeful spirits of jilted brides—Giselle's enduring love protects her faithless lover from death. With its ethereal second act, demanding technical challenges, and profound emotional resonance, Giselle remains one of ballet's greatest achievements.",
                    image: "https://placehold.co/800x400?text=ABT+Giselle",
                    videoUrl: "https://www.youtube.com/embed/eSx_kqe6ox0",
                    isCurrent: false,
                    isNext: false
                },
                {
                    id: "abt-5",
                    title: "The Nutcracker",
                    company: "abt",
                    startDate: "2025-12-12",
                    endDate: "2025-12-31",
                    description: "Alexei Ratmansky's enchanting production of The Nutcracker for American Ballet Theatre brings fresh perspective to this holiday classic. Set to Tchaikovsky's beloved score, the ballet follows young Clara's journey through a magical Christmas Eve adventure. From the festive party scene to the Land of Snow and the Kingdom of Sweets, Ratmansky's choreography combines classical precision with imaginative storytelling. With whimsical designs by Richard Hudson inspired by 19th-century art and literature, ABT's Nutcracker delights audiences of all ages with its charm, humor, and spectacular dancing.",
                    image: "https://placehold.co/800x400?text=ABT+Nutcracker",
                    videoUrl: "https://www.youtube.com/embed/YR5USHu6D6U",
                    isCurrent: false,
                    isNext: false
                }
            ]
        }
    };
    
    return {
        getCompanyInfo: (companyId) => data.companies[companyId] || null,
        getCompanyPerformances: (companyId) => data.performances[companyId] || [],
        getAllCompanies: () => Object.values(data.companies),
        getAllPerformances: () => {
            const allPerformances = [];
            Object.keys(data.performances).forEach(companyId => {
                data.performances[companyId].forEach(performance => {
                    allPerformances.push({
                        ...performance,
                        companyName: data.companies[companyId].name,
                        companyShortName: data.companies[companyId].shortName
                    });
                });
            });
            return allPerformances;
        },
        getAllCurrentPerformances: () => {
            const currentPerformances = [];
            const currentDate = new Date();
            
            Object.keys(data.performances).forEach(companyId => {
                const companyPerformances = data.performances[companyId];
                
                companyPerformances.forEach(performance => {
                    const startDate = new Date(performance.startDate);
                    const endDate = new Date(performance.endDate);
                    
                    // Include performances that are currently running or starting within 30 days
                    if (
                        (currentDate >= startDate && currentDate <= endDate) || 
                        (startDate > currentDate && startDate <= new Date(currentDate.getTime() + 30 * 24 * 60 * 60 * 1000))
                    ) {
                        currentPerformances.push({
                            ...performance,
                            companyName: data.companies[companyId].name,
                            companyShortName: data.companies[companyId].shortName
                        });
                    }
                });
            });
            
            // Sort by start date
            currentPerformances.sort((a, b) => new Date(a.startDate) - new Date(b.startDate));
            
            return currentPerformances;
        },
        getFeaturedPerformances: (count = 3) => {
            const currentPerformances = [];
            const currentDate = new Date();
            
            Object.keys(data.performances).forEach(companyId => {
                const companyPerformances = data.performances[companyId];
                
                companyPerformances.forEach(performance => {
                    const startDate = new Date(performance.startDate);
                    const endDate = new Date(performance.endDate);
                    
                    // Include performances that are currently running or starting within 30 days
                    if (
                        (currentDate >= startDate && currentDate <= endDate) || 
                        (startDate > currentDate && startDate <= new Date(currentDate.getTime() + 30 * 24 * 60 * 60 * 1000))
                    ) {
                        currentPerformances.push({
                            ...performance,
                            companyName: data.companies[companyId].name,
                            companyShortName: data.companies[companyId].shortName
                        });
                    }
                });
            });
            
            // Sort by start date
            currentPerformances.sort((a, b) => new Date(a.startDate) - new Date(b.startDate));
            
            return currentPerformances.slice(0, count);
        }
    };
})();
