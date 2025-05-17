#!/bin/bash
# Script to run the Bolshoi Theatre scraper with different options

# Set default values
USE_WEB=false
USE_SELENIUM=false
SCRAPE_DETAILS=false
OUTPUT_FILE="bolshoi_performances_latest.json"
HTML_FILE="../Bolshoi HTML TEST/Bolshoi Theatre • Season.html"
SKIP_DB=false

# Display help message
show_help() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -w, --web           Scrape directly from the web instead of using a local file"
    echo "  -s, --selenium      Use Selenium for web scraping (for JavaScript-heavy pages)"
    echo "  -d, --details       Scrape detailed information for each performance"
    echo "  -o, --output FILE   Path to save JSON output (default: bolshoi_performances_latest.json)"
    echo "  -f, --file FILE     Path to the HTML file to process (default: ../Bolshoi HTML TEST/Bolshoi Theatre • Season.html)"
    echo "  --no-db             Skip storing in MongoDB"
    echo "  -h, --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -w -s -d -o bolshoi_performances.json  # Scrape from web with Selenium and details"
    echo "  $0 -f local_file.html -o output.json      # Process a local file"
    echo ""
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -w|--web)
            USE_WEB=true
            shift
            ;;
        -s|--selenium)
            USE_SELENIUM=true
            shift
            ;;
        -d|--details)
            SCRAPE_DETAILS=true
            shift
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        -f|--file)
            HTML_FILE="$2"
            shift 2
            ;;
        --no-db)
            SKIP_DB=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Build the command
CMD="python3 bolshoi_scraper.py"

if $USE_WEB; then
    CMD="$CMD --use_web"
fi

if $USE_SELENIUM; then
    CMD="$CMD --use_selenium"
fi

if $SCRAPE_DETAILS; then
    CMD="$CMD --scrape_details"
fi

if $SKIP_DB; then
    CMD="$CMD --no-db"
fi

CMD="$CMD --html_file \"$HTML_FILE\" --output \"$OUTPUT_FILE\""

# Display the command
echo "Running: $CMD"

# Execute the command
eval $CMD

# Check if the command was successful
if [ $? -eq 0 ]; then
    echo "Scraping completed successfully!"
    echo "Output saved to: $OUTPUT_FILE"
else
    echo "Scraping failed with error code: $?"
fi
