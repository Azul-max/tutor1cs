c
import streamlit as st
import pandas as pd
import random
import os



st.set_page_config(
    page_title="TV Scheduling Using Genetic Algorithm",
    page_icon="📺",
    layout="wide"
)

st.title("📺 TV Scheduling Using Genetic Algorithm")

st.write(
    "A Genetic Algorithm application to generate "
    "TV schedules based on audience ratings."
)



GEN = 100
POP = 50
EL_S = 2


# ==========================================
# LOAD CSV DATASET
# ==========================================

from pathlib import Path

# Get the folder where app.py is located
BASE_DIR = Path(__file__).resolve().parent

# Get the exact CSV location
CSV_FILE = BASE_DIR / "program_ratings_modified_final.csv"


@st.cache_data
def load_dataset():

    # Check whether the CSV exists
    if not CSV_FILE.exists():

        st.error("CSV dataset not found!")

        st.write("Files available in the application folder:")

        st.write([
            file.name for file in BASE_DIR.iterdir()
        ])

        return None

    # Read CSV file
    df = pd.read_csv(CSV_FILE)

    ratings = {}

    for _, row in df.iterrows():

        program = row["Type of Program"]

        ratings[program] = [
            float(row[f"Hour {hour}"])
            for hour in range(6, 24)
        ]

    return df, ratings


dataset = load_dataset()

if dataset is None:
    st.stop()

df, ratings = dataset

all_programs = list(ratings.keys())

st.success("Dataset loaded successfully!")


TIME_SLOTS = list(range(6, 24))


def fitness_function(schedule):

    total_rating = 0

    for index, program in enumerate(schedule):

        total_rating += ratings[program][index]

    return total_rating



def initialize_population(programs, population_size):

    population = []

    for _ in range(population_size):

        individual = programs.copy()

        random.shuffle(individual)

        population.append(individual)

    return population



def selection(population):

    fitness_values = [
        fitness_function(individual)
        for individual in population
    ]

    selected = random.choices(
        population,
        weights=fitness_values,
        k=2
    )

    return selected[0], selected[1]




def crossover(parent1, parent2, CO_R):

    if random.random() < CO_R:

        point = random.randint(1, len(parent1) - 1)

        child = parent1[:point]

        for program in parent2:

            if program not in child:
                child.append(program)

        return child

    return parent1.copy()




def mutate(individual, MUT_R):

    individual = individual.copy()

    if random.random() < MUT_R:

        index1, index2 = random.sample(
            range(len(individual)), 2
        )

        individual[index1], individual[index2] = (
            individual[index2],
            individual[index1]
        )

    return individual


# ==========================================
# GENETIC ALGORITHM
# ==========================================

def genetic_algorithm(CO_R, MUT_R, seed=42):

    random.seed(seed)

    population = initialize_population(
        all_programs,
        POP
    )

    best_history = []

    for generation in range(GEN):

        # Sort population by fitness
        population = sorted(
            population,
            key=fitness_function,
            reverse=True
        )

        # Elitism
        new_population = population[:EL_S]

        # Generate new population
        while len(new_population) < POP:

            parent1, parent2 = selection(population)

            child = crossover(
                parent1,
                parent2,
                CO_R
            )

            child = mutate(
                child,
                MUT_R
            )

            new_population.append(child)

        population = new_population

        # Record best fitness
        current_best = max(
            fitness_function(individual)
            for individual in population
        )

        best_history.append(current_best)

    # Find best individual
    best_schedule = max(
        population,
        key=fitness_function
    )

    return best_schedule, best_history




def generate_full_schedule(best_schedule):

    # The GA produces an arrangement of 10 programmes.
    # The first 8 programmes are repeated to fill
    # the remaining 8 time slots.

    full_schedule = best_schedule + best_schedule[:8]

    return full_schedule




def create_schedule_table(schedule):

    schedule_data = []

    for index, program in enumerate(schedule):

        hour = TIME_SLOTS[index]

        audience_rating = ratings[program][index]

        schedule_data.append({
            "Time": f"{hour:02d}:00",
            "Programme": program,
            "Audience Rating": audience_rating
        })

    return pd.DataFrame(schedule_data)


st.header("⚙️ Experiment Configuration")

st.write(
    "Adjust the crossover rate and mutation rate "
    "for each experiment."
)

col1, col2, col3 = st.columns(3)

with col1:

    st.subheader("Experiment 1")

    co1 = st.slider(
        "Crossover Rate",
        0.0, 0.95, 0.50, 0.05,
        key="co1"
    )

    mut1 = st.slider(
        "Mutation Rate",
        0.01, 0.20, 0.05, 0.01,
        key="mut1"
    )


with col2:

    st.subheader("Experiment 2")

    co2 = st.slider(
        "Crossover Rate",
        0.0, 0.95, 0.80, 0.05,
        key="co2"
    )

    mut2 = st.slider(
        "Mutation Rate",
        0.01, 0.20, 0.10, 0.01,
        key="mut2"
    )


with col3:

    st.subheader("Experiment 3")

    co3 = st.slider(
        "Crossover Rate",
        0.0, 0.95, 0.95, 0.05,
        key="co3"
    )

    mut3 = st.slider(
        "Mutation Rate",
        0.01, 0.20, 0.20, 0.01,
        key="mut3"
    )


if st.button(
    "🚀 Run All Experiments",
    type="primary"
):

    experiment_parameters = [
        (co1, mut1),
        (co2, mut2),
        (co3, mut3)
    ]

    results = []

    for i, (co_rate, mut_rate) in enumerate(
        experiment_parameters
    ):

        with st.spinner(
            f"Running Experiment {i + 1}..."
        ):

            best_schedule, history = genetic_algorithm(
                co_rate,
                mut_rate,
                seed=42 + i
            )

            full_schedule = generate_full_schedule(
                best_schedule
            )

            schedule_df = create_schedule_table(
                full_schedule
            )

            total_rating = schedule_df[
                "Audience Rating"
            ].sum()

            results.append({
                "Experiment": f"Experiment {i + 1}",
                "Crossover Rate": co_rate,
                "Mutation Rate": mut_rate,
                "Total Rating": round(total_rating, 2),
                "Schedule": schedule_df,
                "History": history
            })



    st.success("All experiments completed!")

    st.header("📊 Experimental Results")

    comparison = pd.DataFrame([
        {
            "Experiment": result["Experiment"],
            "Crossover Rate": result["Crossover Rate"],
            "Mutation Rate": result["Mutation Rate"],
            "Total Rating": result["Total Rating"]
        }
        for result in results
    ])

    st.dataframe(
        comparison,
        use_container_width=True,
        hide_index=True
    )



    best_result = max(
        results,
        key=lambda result: result["Total Rating"]
    )

    st.header("🏆 Best Experiment")

    st.metric(
        label="Highest Total Audience Rating",
        value=best_result["Total Rating"]
    )

    st.write(
        f"**Experiment:** {best_result['Experiment']}"
    )

    st.write(
        f"**Crossover Rate:** "
        f"{best_result['Crossover Rate']}"
    )

    st.write(
        f"**Mutation Rate:** "
        f"{best_result['Mutation Rate']}"
    )



    st.header("📺 Generated TV Schedules")

    for result in results:

        with st.expander(
            f"{result['Experiment']} "
            f"- Total Rating: {result['Total Rating']}"
        ):

            st.dataframe(
                result["Schedule"],
                use_container_width=True,
                hide_index=True
            )

            st.subheader("Fitness History")

            history_df = pd.DataFrame({
                "Generation": range(1, GEN + 1),
                "Best Fitness": result["History"]
            })

            st.line_chart(
                history_df,
                x="Generation",
                y="Best Fitness"
            )


    st.header("📥 Download Experiment Results")

    download_df = pd.concat(
        [
            result["Schedule"].assign(
                Experiment=result["Experiment"]
            )
            for result in results
        ],
        ignore_index=True
    )

    csv_data = download_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Download All Schedules (CSV)",
        data=csv_data,
        file_name="tv_scheduling_results.csv",
        mime="text/csv"
    )


with st.expander("📄 View Modified Dataset"):

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

st.divider()

st.caption(
    "TV Scheduling Using Genetic Algorithm | "
    "Evolutionary Computing Assignment"
)
