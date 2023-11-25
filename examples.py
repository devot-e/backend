# Plots using matplotlib and seaborn: 
        # generated_stats = generated_data.describe()
        
        # pdf_filename=f"first_app/plots/{file_name}.pdf"
        # with PdfPages(pdf_filename) as pdf:

        #     for i, col in enumerate(real_data.columns):
        #         # Set up subplots
        #         fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(6, 4))

        #         # Plot real data
        #         sns.histplot(real_data[col], kde=True, ax=axes[0])
        #         axes[0].set_title(f'Real Data - {col}')

        #         # Plot generated data
        #         sns.histplot(generated_data[col], kde=True, ax=axes[1])
        #         axes[1].set_title(f'Generated Data - {col}')

        #         # Plot boxplots for real and generated data
        #         sns.boxplot(x='variable', y='value', data=pd.melt(pd.concat([real_data[col], generated_data[col]], axis=1)),
        #                     ax=axes[2])
        #         axes[2].set_title(f'Boxplots - {col}')

        #         # Adjust layout to fit content within the page boundaries
        #         plt.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95, wspace=0.3, hspace=0.4)


        #         # Save the subplot to the PDF
        #         # plt.tight_layout()
        #         pdf.savefig(fig)
        #         plt.close(fig)  # Close the current figure to free up memory
        # print(f'Plots saved to {pdf_filename}')



# plot using table_evaluator

        # table_evaluator = TableEvaluator(df,new_data)
        # table_evaluator.visual_evaluation()

        # Generate the plot using a method from TableEvaluator (replace with actual method name)
        # plot = table_evaluator.generate_plot()

        # Save the plot as a PNG file
        # image_path = os.path.join(base_dir, "first_app", "plots", "plot.png")
        # plot.savefig(image_path, format='png')

        # plt.savefig('myfig')
        # return JsonResponse({'res':'plot created'}, status=200)
