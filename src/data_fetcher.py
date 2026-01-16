import httpx
import json
import pandas as pd
from pathlib import Path

class ExerciseDataFetcher:
    """Fetch and process exercise datasets for Gymmando using httpx"""
    
    def __init__(self, output_dir="exercise_data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.github_url = "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/dist/exercises.json"
        
    def fetch_github_exercises(self):
        """Fetch exercises from GitHub using httpx"""
        print("Fetching exercises from GitHub...")
        
        with httpx.Client(timeout=30.0) as client:
            response = client.get(self.github_url)
            response.raise_for_status()
            exercises = response.json()
        
        print(f"✓ Fetched {len(exercises)} exercises from GitHub")
        
        # Save to JSON
        output_path = self.output_dir / "github_exercises.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(exercises, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved to {output_path}")
        
        # Save as CSV
        df = pd.json_normalize(exercises)
        csv_path = self.output_dir / "github_exercises.csv"
        df.to_csv(csv_path, index=False)
        print(f"✓ Saved CSV to {csv_path}")
        
        return exercises
    
    def analyze_exercises(self, exercises):
        """Analyze the exercise dataset"""
        df = pd.json_normalize(exercises)
        
        print("\n" + "="*60)
        print("DATASET ANALYSIS")
        print("="*60)
        
        print(f"\nTotal Exercises: {len(exercises)}")
        print(f"\nColumns: {list(df.columns)}")
        
        # Analyze by equipment
        if 'equipment' in df.columns:
            print("\nExercises by Equipment:")
            print(df['equipment'].value_counts())
        
        # Analyze by level
        if 'level' in df.columns:
            print("\nExercises by Level:")
            print(df['level'].value_counts())
        
        # Analyze by primary muscles
        if 'primaryMuscles' in df.columns:
            all_muscles = []
            for muscles in df['primaryMuscles']:
                if isinstance(muscles, list):
                    all_muscles.extend(muscles)
            muscle_counts = pd.Series(all_muscles).value_counts()
            print("\nExercises by Primary Muscle:")
            print(muscle_counts)
        
        return df
    
    def filter_exercises(self, exercises, equipment=None, level=None, muscle=None):
        """Filter exercises by criteria"""
        filtered = exercises
        
        if equipment:
            filtered = [e for e in filtered if e.get('equipment') == equipment]
        
        if level:
            filtered = [e for e in filtered if e.get('level') == level]
        
        if muscle:
            filtered = [e for e in filtered 
                       if muscle in e.get('primaryMuscles', [])]
        
        return filtered
    
    def get_exercise_by_name(self, exercises, name):
        """Get a specific exercise by name"""
        name_lower = name.lower()
        for exercise in exercises:
            if name_lower in exercise.get('name', '').lower():
                return exercise
        return None
    
    def export_for_gymmando(self, exercises, output_file="gymmando_exercises.json"):
        """Export exercises in a format optimized for Gymmando"""
        # Create a simplified structure for your app
        gymmando_format = []
        
        for ex in exercises:
            simplified = {
                'id': ex.get('id'),
                'name': ex.get('name'),
                'equipment': ex.get('equipment'),
                'level': ex.get('level'),
                'primaryMuscles': ex.get('primaryMuscles', []),
                'secondaryMuscles': ex.get('secondaryMuscles', []),
                'instructions': ex.get('instructions', []),
                'category': ex.get('category'),
                'force': ex.get('force'),
                'mechanic': ex.get('mechanic')
            }
            gymmando_format.append(simplified)
        
        output_path = self.output_dir / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(gymmando_format, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Exported {len(gymmando_format)} exercises for Gymmando")
        print(f"✓ Saved to {output_path}")
        
        return gymmando_format


# Example usage
if __name__ == "__main__":
    fetcher = ExerciseDataFetcher()
    
    # Fetch data
    exercises = fetcher.fetch_github_exercises()
    
    # Analyze
    df = fetcher.analyze_exercises(exercises)
    
    # Example filtering
    print("\n" + "="*60)
    print("EXAMPLE FILTERS")
    print("="*60)
    
    dumbbell_exercises = fetcher.filter_exercises(exercises, equipment='dumbbell')
    print(f"\nDumbbell exercises: {len(dumbbell_exercises)}")
    
    beginner_exercises = fetcher.filter_exercises(exercises, level='beginner')
    print(f"Beginner exercises: {len(beginner_exercises)}")
    
    chest_exercises = fetcher.filter_exercises(exercises, muscle='chest')
    print(f"Chest exercises: {len(chest_exercises)}")
    
    # Example: Get specific exercise
    bench_press = fetcher.get_exercise_by_name(exercises, "bench press")
    if bench_press:
        print(f"\nFound exercise: {bench_press['name']}")
        print(f"Instructions: {len(bench_press.get('instructions', []))} steps")
    
    # Export for Gymmando
    fetcher.export_for_gymmando(exercises)