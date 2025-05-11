class NewsGame {
    constructor() {
        this.currentRound = 1;
        this.score = 0;
        this.maxRounds = 5;
        this.triplets = [];
        this.currentTripletIndex = 0;
        this.gameStarted = false;
    }

    // Fisher-Yates shuffle algorithm
    shuffle(array) {
        const shuffled = [...array];
        for (let i = shuffled.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
        }
        return shuffled;
    }

    showIntroduction() {
        const gameContent = document.getElementById('game-content');
        gameContent.innerHTML = `
            <div class="text-center introduction">
                <h2 class="mb-4">ברוכים הבאים למשחק!</h2>
                <p class="mb-4">חושבים שאתם יכולים לזהות את המקור החדשותי על פי הכותרת?</p>
                <div class="game-instructions mb-4">
                    <h4>מהלך המשחק:</h4>
                    <p>בכל סיבוב יוצג לכם מבזק ממקורות שונים, אם תצליחו לנחש מאיזה מקור מגיעה אחת הכותרות, תזכו בנקודה.</p>
                </div>
                <button class="btn btn-primary btn-lg" onclick="game.startGame()">התחל משחק</button>
            </div>
        `;
    }

    async startGame() {
        this.gameStarted = true;
        this.currentRound = 1;
        this.score = 0;
        this.currentTripletIndex = 0;
        this.updateGameStatus();
        await this.loadTriplets();
    }

    updateGameStatus() {
        document.getElementById('current-round').textContent = this.currentRound;
        document.getElementById('score').textContent = this.score;
    }

    async loadTriplets() {
        try {
            const response = await fetch('/api/game/triplets');
            this.triplets = await response.json();
            this.displayCurrentTriplet();
        } catch (error) {
            console.error('Error loading triplets:', error);
        }
    }

    displayCurrentTriplet() {
        if (this.currentTripletIndex >= this.triplets.length) {
            this.endGame();
            return;
        }

        const currentTriplet = this.triplets[this.currentTripletIndex];
        const gameContent = document.getElementById('game-content');
        gameContent.innerHTML = '';

        // Get unique sources from the current triplet
        const availableSources = [...new Set(currentTriplet.articles.map(article => article.source))];
        const randomNumber = Math.floor(Math.random() * availableSources.length);
        const i = 0
        currentTriplet.articles.forEach((article, index) => {
            const articleDiv = document.createElement('div');
            articleDiv.className = 'game-article';
            
            // Create button objects with source and text
            const buttonObjects = availableSources.map(source => {
                const buttonText = {
                    'Haaretz': 'הארץ',
                    'Ynet': 'ynet',
                    'Walla': 'וואלה',
                    'IsraelHayom': 'ישראל היום'
                }[source] || source;
                
                return {
                    source: source,
                    text: buttonText
                };
            });
            
            // Shuffle the button objects
            const shuffledButtons = this.shuffle(buttonObjects);
            
            // Create HTML for the shuffled buttons
            const sourceButtons = shuffledButtons.map(button => 
                `<button class="btn btn-outline-primary" onclick="game.checkAnswer(${index}, '${button.source}')">${button.text}</button>`
            ).join('');

            articleDiv.innerHTML = `
                <h4>${article.title}</h4>
                <div class="source-buttons">
                    ${sourceButtons}
                </div>
            `;
            // present only one random article of the triplet
            if (i == randomNumber) { 
                gameContent.appendChild(articleDiv);
            }
            i++;
        });
    }

    async checkAnswer(articleIndex, selectedSource) {
        const currentTriplet = this.triplets[this.currentTripletIndex];
        const correctSource = currentTriplet.articles[articleIndex].source;
        const isCorrect = selectedSource === correctSource;

        if (isCorrect) {
            this.score++;
            this.updateGameStatus();
        }

        // Show feedback
        const buttons = document.querySelectorAll('.source-buttons button');
        buttons.forEach(button => {
            button.disabled = true;
            if (button.textContent === correctSource) {
                button.classList.add('btn-success');
            }
        });

        // Wait a moment before moving to next round
        setTimeout(() => {
            if (this.currentRound < this.maxRounds) {
                this.currentRound++;
                this.currentTripletIndex++;
                this.updateGameStatus();
                this.displayCurrentTriplet();
            } else {
                this.endGame();
            }
        }, 1500);
    }

    endGame() {
        const gameContent = document.getElementById('game-content');
        gameContent.innerHTML = `
            <div class="text-center">
                <h3>המשחק הסתיים!</h3>
                <p>הניקוד הסופי שלך: ${this.score} מתוך ${this.maxRounds}</p>
                <button class="btn btn-primary" onclick="game.startGame()">שחק שוב</button>
            </div>
        `;
    }
}

class NewsComparison {
    constructor() {
        this.triplets = [];
    }

    async loadTriplets() {
        try {
            const response = await fetch('/api/comparison/triplets');
            this.triplets = await response.json();
            this.displayTriplets();
        } catch (error) {
            console.error('Error loading triplets:', error);
        }
    }

    displayTriplets() {
        const container = document.getElementById('news-triplets');
        container.innerHTML = '';

        this.triplets.forEach(triplet => {
            const tripletDiv = document.createElement('div');
            tripletDiv.className = 'col-12 mb-4';
            
            const articlesHtml = triplet.articles.map(article => `
                <div class="col-md-4">
                    <div class="news-card source-${article.source}">
                        <h5>${article.title}</h5>
                        <div class="source">${article.source}</div>
                        <div class="datetime">${new Date(article.datetime).toLocaleString('he-IL')}</div>
                        <a href="${article.url}" target="_blank" class="btn btn-primary">קרא עוד</a>
                    </div>
                </div>
            `).join('');

            tripletDiv.innerHTML = `
                <div class="row">
                    ${articlesHtml}
                </div>
            `;
            container.appendChild(tripletDiv);
        });
    }
}

// Initialize the game and comparison
const game = new NewsGame();
const comparison = new NewsComparison();

// Show introduction when the page loads
document.addEventListener('DOMContentLoaded', () => {
    game.showIntroduction();
    comparison.loadTriplets();
});

// Handle tab changes
document.querySelectorAll('button[data-bs-toggle="tab"]').forEach(tab => {
    tab.addEventListener('shown.bs.tab', (e) => {
        if (e.target.id === 'comparison-tab') {
            comparison.loadTriplets();
        }
    });
}); 