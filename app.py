
import streamlit as st
import pandas as pd
import csv
import random
import itertools
import os

st.set_page_config(
    page_title="TV Scheduling - Genetic Algorithm",
    page_icon="📺",
    layout="wide"
)

st.title("📺 TV Scheduling Using Genetic Algorithm")
st.write(
    "Adjust the Genetic Algorithm parameters and "
    "generate television schedules."
)

CSV_FILE = "program_ratings_modified.csv"

if not os.path.exists(CSV_FILE):
    st.error(
        f"CSV file '{CSV_FILE}' was not found. "
        "Please place it in the same folder as app.py."
    )
    st.stop()


def read_csv_to_dict(file_path):
    program_ratings = {}

    with open(file_path, mode="r", newline="") as file:
        reader = csv.reader(file)
        header = next(reader)

        for row in reader:
            program = row[0]
            ratings = [float(x) for x in row[1:]]
            program_ratings[program] = ratings

    return program_ratings


ratings = read_csv_to_dict(CSV_FILE)

all_programs = list(ratings.keys())
all_time_slots = list(range(6, 24))


GEN = 100
POP = 50
EL_S = 2

def fitness_function(schedule):
    total_rating = 0

    for time_slot, program in enumerate(schedule):
        total_rating += ratings[program][time_slot]

    return total_rating


@st.cache_data
def get_initial_best_schedule(ratings_data):

    rating_dict = {
        program: list(program_ratings)
        for program, program_ratings in ratings_data
    }

    programs = list(rating_dict.keys())

    def calculate_fitness(schedule):
        total_rating = 0

        for time_slot, program in enumerate(schedule):
            total_rating += rating_dict[program][time_slot]

        return total_rating

    best_schedule = max(
        itertools.permutations(programs),
        key=calculate_fitness
    )

    return list(best_schedule)


ratings_data = tuple(
    (program, tuple(values))
    for program, values in ratings.items()
)

initial_best_schedule = get_initial_best_schedule(ratings_data)


def crossover(schedule1, schedule2):

    crossover_point = random.randint(
        1, len(schedule1) - 2
    )

    child1 = (
        schedule1[:crossover_point]
        + schedule2[crossover_point:]
    )

    child2 = (
        schedule2[:crossover_point]
        + schedule1[crossover_point:]
    )

    return child1, child2


def mutate(schedule):

    mutation_point = random.randint(
        0, len(schedule) - 1
    )

    new_program = random.choice(all_programs)

    schedule[mutation_point] = new_program

    return schedule


def evaluate_fitness(schedule):
    return fitness_function(schedule)


def genetic_algorithm(
    initial_schedule,
    generations=GEN,
    population_size=POP,
    crossover_rate=0.8,
    mutation_rate=0.03,
    elitism_size=EL_S
):

    population = [initial_schedule]

    for _ in range(population_size - 1):

        random_schedule = initial_schedule.copy()

        random.shuffle(random_schedule)

        population.append(random_schedule)

    for generation in range(generations):

        new_population = []

        population.sort(
            key=lambda schedule: fitness_function(schedule),
            reverse=True
        )

        new_population.extend(
            population[:elitism_size]
        )

        while len(new_population) < population_size:

            parent1, parent2 = random.choices(
                population,
                k=2
            )

            if random.random() < crossover_rate:

                child1, child2 = crossover(
                    parent1, parent2
                )

            else:

                child1 = parent1.copy()
                child2 = parent2.copy()

            if random.random() < mutation_rate:
                child1 = mutate(child1)

            if random.random() < mutation_rate:
                child2 = mutate(child2)

            new_population.extend(
                [child1, child2]
            )

        population = new_population

    return population[0]


def run_experiment(crossover_rate, mutation_rate):

    genetic_schedule = genetic_algorithm(
        initial_best_schedule,
        generations=GEN,
        population_size=POP,
        crossover_rate=crossover_rate,
        mutation_rate=mutation_rate,
        elitism_size=EL_S
    )

    remaining_slots = (
        len(all_time_slots) - len(initial_best_schedule)
    )

    final_schedule = (
        initial_best_schedule
        + genetic_schedule[:remaining_slots]
    )

    total_rating = fitness_function(final_schedule)

    schedule_data = []

    for time_slot, program in enumerate(final_schedule):

        schedule_data.append({
            "Time": f"{all_time_slots[time_slot]:02d}:00",
            "Program": program,
            "Rating": ratings[program][time_slot]
        })

    return total_rating, pd.DataFrame(schedule_data)


# ==========================================
# 11. STREAMLIT INTERFACE
# ==========================================

st.divider()

st.subheader("Experiment Parameters")

st.write(
    "Enter different crossover and mutation rates "
    "for each experiment."
)

col1, col2, col3 = st.columns(3)

with col1:

    st.markdown("### Trial 1")

    co1 = st.slider(
        "Crossover Rate - Trial 1",
        min_value=0.0,
        max_value=0.95,
        value=0.50,
        step=0.05
    )

    mut1 = st.slider(
        "Mutation Rate - Trial 1",
        min_value=0.01,
        max_value=0.05,
        value=0.01,
        step=0.01
    )


with col2:

    st.markdown("### Trial 2")

    co2 = st.slider(
        "Crossover Rate - Trial 2",
        min_value=0.0,
        max_value=0.95,
        value=0.80,
        step=0.05
    )

    mut2 = st.slider(
        "Mutation Rate - Trial 2",
        min_value=0.01,
        max_value=0.05,
        value=0.03,
        step=0.01
    )


with col3:

    st.markdown("### Trial 3")

    co3 = st.slider(
        "Crossover Rate - Trial 3",
        min_value=0.0,
        max_value=0.95,
        value=0.95,
        step=0.05
    )

    mut3 = st.slider(
        "Mutation Rate - Trial 3",
        min_value=0.01,
        max_value=0.05,
        value=0.05,
        step=0.01
    )


st.divider()

if st.button(
    "▶ Run Genetic Algorithm",
    type="primary",
    use_container_width=True
):

    experiments = [
        ("Trial 1", co1, mut1),
        ("Trial 2", co2, mut2),
        ("Trial 3", co3, mut3)
    ]

    results = []

    progress = st.progress(0)

    for index, (trial_name, co_rate, mut_rate) in enumerate(experiments):

        # Use a consistent random seed for comparison
        random.seed(42)

        total_rating, schedule_table = run_experiment(
            co_rate,
            mut_rate
        )

        results.append({
            "Trial": trial_name,
            "Crossover Rate": co_rate,
            "Mutation Rate": mut_rate,
            "Total Rating": total_rating,
            "Schedule": schedule_table
        })

        progress.progress((index + 1) / 3)

    st.success("All three experiments completed!")

    st.subheader("Experiment Comparison")

    comparison_data = []

    for result in results:

        comparison_data.append({
            "Trial": result["Trial"],
            "Crossover Rate": result["Crossover Rate"],
            "Mutation Rate": result["Mutation Rate"],
            "Total Rating": result["Total Rating"]
        })

    comparison_table = pd.DataFrame(comparison_data)

    st.dataframe(
        comparison_table,
        use_container_width=True,
        hide_index=True
    )


    st.subheader("Generated Television Schedules")

    for result in results:

        st.markdown(f"### {result['Trial']}")

        st.write(
            f"Crossover Rate: {result['Crossover Rate']} | "
            f"Mutation Rate: {result['Mutation Rate']}"
        )

        st.metric(
            "Total Rating",
            f"{result['Total Rating']:.2f}"
        )

        st.dataframe(
            result["Schedule"],
            use_container_width=True,
            hide_index=True
        )

  
    best_trial = max(
        results,
        key=lambda result: result["Total Rating"]
    )

    st.divider()

    st.subheader("Best Performing Trial")

    st.success(
        f"Best Result: {best_trial['Trial']}"
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Crossover Rate",
        best_trial["Crossover Rate"]
    )

    col2.metric(
        "Mutation Rate",
        best_trial["Mutation Rate"]
    )

    col3.metric(
        "Highest Total Rating",
        f"{best_trial['Total Rating']:.2f}"
    )

    st.subheader("Download Results")

    csv_results = comparison_table.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Download Comparison Results",
        data=csv_results,
        file_name="GA_experiment_results.csv",
        mime="text/csv"
    )

else:

    st.info(
        "Adjust the parameters above and click "
        "'Run Genetic Algorithm' to generate the schedules."
    )
