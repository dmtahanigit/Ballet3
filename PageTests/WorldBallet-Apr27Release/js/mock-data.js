/**
 * Ballet World - Mock Data
 * 
 * This module provides mock data for development and testing purposes.
 * It serves as a fallback when the API is unavailable.
 */

const MockData = (() => {
    // Mock company data
    const companies = [
        {
            id: 'paris_opera_ballet',
            name: 'Paris Opera Ballet',
            shortName: 'POB',
            description: 'The Paris Opera Ballet is the oldest national ballet company in the world, and many European and international ballet companies can trace their origins to it. It has been an integral part of the Paris Opera since 1669, when the company was founded under Louis XIV as the Académie d\'Opéra, then renamed the Académie Royale de Danse.',
            logo: 'https://placehold.co/150x150?text=POB+Logo',
            website: 'https://www.operadeparis.fr/en/artists/ballet',
            location: 'Paris, France',
            founded: 1669
        },
        {
            id: 'bolshoi_ballet',
            name: 'Bolshoi Ballet',
            shortName: 'Bolshoi',
            description: 'The Bolshoi Ballet is an internationally renowned classical ballet company, based at the Bolshoi Theatre in Moscow, Russia. Founded in 1776, the Bolshoi is among the world\'s oldest ballet companies. It achieved worldwide acclaim after the October Revolution of 1917 when the theatre was nationalized.',
            logo: 'https://placehold.co/150x150?text=Bolshoi+Logo',
            website: 'https://www.bolshoi.ru/en/',
            location: 'Moscow, Russia',
            founded: 1776
        },
        {
            id: 'royal_ballet',
            name: 'The Royal Ballet',
            shortName: 'Royal Ballet',
            description: 'The Royal Ballet is an internationally renowned classical ballet company, based at the Royal Opera House in Covent Garden, London, England. The company employs about 100 dancers and has purpose-built facilities within the Royal Opera House.',
            logo: 'https://placehold.co/150x150?text=Royal+Ballet+Logo',
            website: 'https://www.roh.org.uk/about/the-royal-ballet',
            location: 'London, UK',
            founded: 1931
        }
    ];

    // Mock performance data for Paris Opera Ballet
    const parisOperaBalletPerformances = [
        {
            id: 'pob_giselle',
            title: 'Giselle',
            description: 'First performed at the Académie royale de Musique in 1841, Giselle was an immediate success. The choreography by Jean Coralli and Jules Perrot, which would be enriched by Marius Petipa, the music by Adolphe Adam and the performances of Carlotta Grisi and Lucien Petipa in the principal roles all contributed to the triumph of this landmark work in the history of dance.',
            image: 'https://placehold.co/800x400?text=Giselle',
            thumbnail: 'https://placehold.co/400x200?text=Giselle',
            startDate: '2025-06-01',
            endDate: '2025-06-15',
            venue: 'Palais Garnier',
            videoUrl: '',
            company: 'paris_opera_ballet',
            isCurrent: true
        },
        {
            id: 'pob_swan_lake',
            title: 'Swan Lake',
            description: 'Swan Lake is a timeless love story that mixes magic, tragedy, and romance into four acts. It features Prince Siegfried and a lovely swan princess named Odette, who is under a spell cast by the evil sorcerer Von Rothbart. The spell can only be broken by a man who has never loved before and who will remain faithful to her forever.',
            image: 'https://placehold.co/800x400?text=Swan+Lake',
            thumbnail: 'https://placehold.co/400x200?text=Swan+Lake',
            startDate: '2025-07-10',
            endDate: '2025-07-25',
            venue: 'Opéra Bastille',
            videoUrl: '',
            company: 'paris_opera_ballet',
            isCurrent: false
        },
        {
            id: 'pob_nutcracker',
            title: 'The Nutcracker',
            description: 'The Nutcracker is a classical ballet in two acts. It is based on E.T.A. Hoffmann\'s 1816 fairy tale "The Nutcracker and the Mouse King". It tells the story of a little girl who goes to the Land of Sweets on Christmas Eve. Ivan Vsevolozhsky and Marius Petipa adapted Hoffmann\'s story for the ballet.',
            image: 'https://placehold.co/800x400?text=Nutcracker',
            thumbnail: 'https://placehold.co/400x200?text=Nutcracker',
            startDate: '2025-12-10',
            endDate: '2025-12-31',
            venue: 'Opéra Bastille',
            videoUrl: '',
            company: 'paris_opera_ballet',
            isCurrent: false
        }
    ];

    // Mock performance data for Bolshoi Ballet
    const bolshoiBalletPerformances = [
        {
            id: 'bolshoi_spartacus',
            title: 'Spartacus',
            description: 'Spartacus is a ballet by Aram Khachaturian. The work follows the exploits of Spartacus, the leader of the slave uprising against the Romans known as the Third Servile War, although the ballet\'s storyline takes considerable liberties with the historical record.',
            image: 'https://placehold.co/800x400?text=Spartacus',
            thumbnail: 'https://placehold.co/400x200?text=Spartacus',
            startDate: '2025-05-20',
            endDate: '2025-06-05',
            venue: 'Bolshoi Theatre',
            videoUrl: '',
            company: 'bolshoi_ballet',
            isCurrent: true
        },
        {
            id: 'bolshoi_sleeping_beauty',
            title: 'The Sleeping Beauty',
            description: 'The Sleeping Beauty is a ballet in a prologue and three acts, first performed in 1890. The music was composed by Pyotr Ilyich Tchaikovsky. The choreography is the original by Marius Petipa. The Sleeping Beauty is the second of his three ballets.',
            image: 'https://placehold.co/800x400?text=Sleeping+Beauty',
            thumbnail: 'https://placehold.co/400x200?text=Sleeping+Beauty',
            startDate: '2025-07-15',
            endDate: '2025-07-30',
            venue: 'Bolshoi Theatre',
            videoUrl: '',
            company: 'bolshoi_ballet',
            isCurrent: false
        },
        {
            id: 'bolshoi_don_quixote',
            title: 'Don Quixote',
            description: 'Don Quixote is a ballet originally staged in four acts and eight scenes, based on episodes taken from the famous novel Don Quixote de la Mancha by Miguel de Cervantes. It was originally choreographed by Marius Petipa to the music of Ludwig Minkus and first presented by the Ballet of the Imperial Bolshoi Theatre of Moscow, Russia in 1869.',
            image: 'https://placehold.co/800x400?text=Don+Quixote',
            thumbnail: 'https://placehold.co/400x200?text=Don+Quixote',
            startDate: '2025-09-10',
            endDate: '2025-09-25',
            venue: 'Bolshoi Theatre',
            videoUrl: '',
            company: 'bolshoi_ballet',
            isCurrent: false
        }
    ];

    // Mock performance data for Royal Ballet
    const royalBalletPerformances = [
        {
            id: 'royal_romeo_juliet',
            title: 'Romeo and Juliet',
            description: 'Romeo and Juliet is a ballet by Sergei Prokofiev based on William Shakespeare\'s play Romeo and Juliet. Prokofiev reused music from the ballet in three suites for orchestra and a solo piano work.',
            image: 'https://placehold.co/800x400?text=Romeo+and+Juliet',
            thumbnail: 'https://placehold.co/400x200?text=Romeo+and+Juliet',
            startDate: '2025-05-15',
            endDate: '2025-06-10',
            venue: 'Royal Opera House',
            videoUrl: '',
            company: 'royal_ballet',
            isCurrent: true
        },
        {
            id: 'royal_alice',
            title: 'Alice\'s Adventures in Wonderland',
            description: 'Alice\'s Adventures in Wonderland is a ballet in three acts by Christopher Wheeldon with a scenario by Nicholas Wright, based on Lewis Carroll\'s classic 1865 children\'s book Alice\'s Adventures in Wonderland. It was commissioned by The Royal Ballet, Covent Garden, and the National Ballet of Canada.',
            image: 'https://placehold.co/800x400?text=Alice+in+Wonderland',
            thumbnail: 'https://placehold.co/400x200?text=Alice+in+Wonderland',
            startDate: '2025-07-20',
            endDate: '2025-08-05',
            venue: 'Royal Opera House',
            videoUrl: '',
            company: 'royal_ballet',
            isCurrent: false
        }
    ];

    // Combine all performances
    const allPerformances = [
        ...parisOperaBalletPerformances,
        ...bolshoiBalletPerformances,
        ...royalBalletPerformances
    ];

    // Get current performances
    const currentPerformances = allPerformances.filter(p => {
        const now = new Date();
        const startDate = new Date(p.startDate);
        const endDate = new Date(p.endDate);
        return (now >= startDate && now <= endDate) || 
               (startDate > now && startDate <= new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000));
    });

    // Public API
    return {
        // Company data
        getCompanyInfo: (companyId) => {
            return companies.find(c => c.id === companyId) || null;
        },
        
        getAllCompanies: () => {
            return companies;
        },
        
        // Performance data
        getCompanyPerformances: (companyId) => {
            switch (companyId) {
                case 'paris_opera_ballet':
                    return parisOperaBalletPerformances;
                case 'bolshoi_ballet':
                    return bolshoiBalletPerformances;
                case 'royal_ballet':
                    return royalBalletPerformances;
                default:
                    return [];
            }
        },
        
        getPerformanceDetails: (companyId, performanceId) => {
            const performances = MockData.getCompanyPerformances(companyId);
            return performances.find(p => p.id === performanceId) || null;
        },
        
        getAllCurrentPerformances: () => {
            return currentPerformances;
        },
        
        // Search functionality
        searchPerformances: (query) => {
            if (!query) return [];
            
            const lowerQuery = query.toLowerCase();
            return allPerformances.filter(p => 
                p.title.toLowerCase().includes(lowerQuery) || 
                p.description.toLowerCase().includes(lowerQuery)
            );
        }
    };
})();
