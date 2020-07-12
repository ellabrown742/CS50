#include <cs50.h>
#include <stdio.h>
#include <string.h>

// Max number of candidates
#define MAX 9

// preferences[i][j] is number of voters who prefer i over j
int preferences[MAX][MAX];

// locked[i][j] means i is locked in over j
bool locked[MAX][MAX];

// Each pair has a winner, loser
typedef struct
{
    int winner;
    int loser;
}
pair;

// Array of candidates
string candidates[MAX];
pair pairs[MAX * (MAX - 1) / 2];

int pair_count;
int candidate_count;

// Function prototypes
bool vote(int rank, string name, int ranks[]);
void record_preferences(int ranks[]);
void add_pairs(void);
void sort_pairs(void);
void lock_pairs(void);
void print_winner(void);
bool determine_cycle(bool visited[], int source, int destination);
bool determine_cycle_h(bool visited[], int source, int destination);

int main(int argc, string argv[])
{
    // Check for invalid usage
    if (argc < 2)
    {
        printf("Usage: tideman [candidate ...]\n");
        return 1;
    }

    // Populate array of candidates
    candidate_count = argc - 1;
    if (candidate_count > MAX)
    {
        printf("Maximum number of candidates is %i\n", MAX);
        return 2;
    }
    for (int i = 0; i < candidate_count; i++)
    {
        candidates[i] = argv[i + 1];
    }
    for (int i = 0; i < candidate_count; i++)
    {
        //printf("%s\n", candidates[i]);
    }

    // Clear graph of locked in pairs
    for (int i = 0; i < candidate_count; i++)
    {
        for (int j = 0; j < candidate_count; j++)
        {
            locked[i][j] = false;
        }
    }

    pair_count = 0;
    int voter_count = get_int("Number of voters: ");

    // Query for votes
    for (int i = 0; i < voter_count; i++)
    {
        // ranks[i] is voter's ith preference
        int ranks[candidate_count];

        // Query for each rank
        for (int j = 0; j < candidate_count; j++)
        {
            string name = get_string("Rank %i: ", j + 1);

            if (!vote(j, name, ranks))
            {
                printf("Invalid vote.\n");
                return 3;
            }
            //printf("%i\n", ranks[j]);
        }
        record_preferences(ranks);
        printf("\n");
    }
    for (int i = 0; i < candidate_count; i++)
    {
        for (int j = 0; j < candidate_count; j++)
        {
            //printf("%i ", preferences[i][j]);
        }
        //printf("\n");
    }

    add_pairs();
    sort_pairs();
    lock_pairs();
    print_winner();
    return 0;
}

// Update ranks given a new vote
bool vote(int rank, string name, int ranks[])
{
    for (int i = 0; i < candidate_count; i++)
    {
        if (!strcmp(name, candidates[i]))
        {
            ranks[rank] = i;
            return true;
        }
    }
    return false;
}

// Update preferences given one voter's ranks
void record_preferences(int ranks[])
{
    for (int i = 0; i < candidate_count; i++)
    {
        for (int j = i; j < candidate_count; j++)
        {
            if (j == i)
            {
                continue;
            }
            preferences[ranks[i]][ranks[j]]++;
        }
    }
}

// Record pairs of candidates where one is preferred over the other
void add_pairs(void)
{
    for (int i = 0; i < candidate_count; i++)
    {
        for (int j = i + 1; j < candidate_count; j++)
        {
            if (preferences[i][j] > preferences[j][i])
            {
                pairs[pair_count].winner = i;
                pairs[pair_count].loser = j;
                pair_count++;
            }
            else if (preferences[j][i] > preferences[i][j])
            {
                pairs[pair_count].winner = j;
                pairs[pair_count].loser = i;
                pair_count++;
            }
        }
    }
    return;
}

// Sort pairs in decreasing order by strength of victory
void sort_pairs(void)
{
    for (int i = 0; i < pair_count; i++)
    {
        int biggest_difference = preferences[pairs[i].winner][pairs[i].loser] - preferences[pairs[i].loser][pairs[i].winner];
        int index = i;
        for (int j = i + 1; j < pair_count; j++)
        {
            if (preferences[pairs[j].winner][pairs[j].loser] - preferences[pairs[j].loser][pairs[j].winner] > biggest_difference)
            {
                biggest_difference = preferences[pairs[j].winner][pairs[j].loser] - preferences[pairs[j].loser][pairs[j].winner];
                index = j;
            }
        }
        pair temp = pairs[index];
        pairs[index] = pairs[i];
        pairs[i] = temp;
    }
}

// Lock pairs into the candidate graph in order, without creating cycles
void lock_pairs(void)
{
    bool visited[candidate_count];
    // for (int i = 0; i < candidate_count; i++)
    // {
    //     visited[i] = false;
    // }
    for (int i = 0; i < pair_count; i++)
    {
        locked[pairs[i].winner][pairs[i].loser] = true;
        if (determine_cycle(visited, pairs[i].winner, pairs[i].loser))
        {
            locked[pairs[i].winner][pairs[i].loser] = false;
        }
        // if (!determine_cycle(visited, pairs[i].winner, pairs[i].loser))
        // {
        //     locked[pairs[i].winner][pairs[i].loser] = true;
        // }
        // else
        // {
        //     locked[pairs[i].winner][pairs[i].loser] = false;
        // }
    }
}

bool determine_cycle(bool visited[], int source, int destination)
{
    //non recursive, calls on recursive function

    for (int i = 0; i < candidate_count; i++)
    {
        visited[i] = false;
    }
    //locked[source][destination] = true;
    for (int i = 0; i < candidate_count; i++)
    {
        if (determine_cycle_h(visited, source, source))
        {
            return true;
        }
    }
    return false;
}

bool determine_cycle_h(bool visited[], int source, int destination)
{
    visited[source] = true;
    if (locked[source][destination] && visited[destination])
    {
        return true;
    }
    for (int i = 0; i < candidate_count; i++)
    {
        if ((locked[source][i]) == true)
        {
            if (determine_cycle_h(visited, i, destination))
            {
                return true;
            }
        }
    }
    return false;
}

// Print the winner of the election
void print_winner(void)
{
    int winner[candidate_count];
    for (int i = 0; i < candidate_count; i++)
    {
        bool source = true;
        for (int j = 0; j < candidate_count; j++)
        {
            if (locked[j][i] == true)
            {
                source = false;
            }
        }
        if (source)
        {
            printf("%s\n", candidates[i]);
            return;
        }
    }

    // for (int i = 0; i < candidate_count; i++)
    // {
    //     winner[i] = 0;
    // }
    // for (int i = 0; i < candidate_count; i++)
    // {
    //     for (int j = 0; j < candidate_count; j++)
    //     {
    //         if (locked[i][j])
    //         {
    //             winner[i]++;
    //         }
    //     }
    // }
    // for (int i = 0; i < candidate_count; i++)
    // {
    //     printf("%i\n", winner[i]);
    // }
    // int final = 0;
    // for (int i = 1; i < candidate_count; i++)
    // {
    //     if (winner[i] > winner[final])
    //     {
    //         final = i;
    //     }
    // }
    // printf("%s\n", candidates[final]);
}

