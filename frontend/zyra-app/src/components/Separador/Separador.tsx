export default function Separador() {
    return (
        <hr
            className="
                mx-auto
                mb-[3.6rem]
                h-[1.5px]
                w-[85%]
                max-w-[1300px]
                border-none
                bg-separator-light

                tablet:mb-[4.2rem]
                tablet:w-[75%]

                desktop:mb-[4.8rem]
                desktop:w-3/5
            "
            aria-hidden="true"
        />
    );
}